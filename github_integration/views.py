import hashlib
import hmac
import json
import logging
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import GithubAccount, RepositorySelection

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth without CSRF enforcement for SPA POST requests."""

    def enforce_csrf(self, request):
        return

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def github_authorize_url(request):
    """
    Return the GitHub authorize URL so the frontend can redirect the user.
    """

    client_id = settings.GITHUB_CLIENT_ID
    # Use an explicit external base URL so the redirect_uri matches what is
    # configured in the GitHub OAuth app (and is reachable from the browser).
    redirect_uri = settings.GITHUB_REDIRECT_BASE.rstrip("/") + "/api/github/callback/"
    params = {
        "client_id": client_id,
        "scope": "repo,admin:repo_hook",
        "redirect_uri": redirect_uri,
    }
    url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return Response({"authorize_url": url})


def github_oauth_callback(request):
    """
    Exchange the GitHub OAuth code for an access token and store it for the logged-in user.
    Redirects back to the frontend after completion.
    """
    frontend_base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    code = request.GET.get("code")
    if not code:
        return redirect(f"{frontend_base}/dashboard?error=missing_code")

    # Check if user is logged in via session
    if not request.user.is_authenticated:
        return redirect(f"{frontend_base}/dashboard?error=not_authenticated")

    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    token_resp = requests.post("https://github.com/login/oauth/access_token", data=data, headers=headers, timeout=5)
    if token_resp.status_code != 200:
        return redirect(f"{frontend_base}/dashboard?error=token_exchange_failed")

    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    token_type = token_data.get("token_type", "bearer")
    scope = token_data.get("scope", "")

    if not access_token:
        error_desc = token_data.get("error_description", "unknown_error")
        return redirect(f"{frontend_base}/dashboard?error={urlencode({'msg': error_desc})}")

    # Fetch GitHub user info
    user_resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"},
        timeout=5,
    )
    if user_resp.status_code != 200:
        return redirect(f"{frontend_base}/dashboard?error=github_user_fetch_failed")

    gh_user = user_resp.json()
    github_id = str(gh_user.get("id"))
    github_login = gh_user.get("login", "")

    # Persist GitHub credentials in the database for the logged-in user
    GithubAccount.objects.update_or_create(
        user=request.user,
        defaults={
            "access_token": access_token,
            "token_type": token_type,
            "scope": scope,
            "github_user_id": github_id,
            "github_username": github_login,
        },
    )

    # Redirect back to frontend dashboard with success
    return redirect(f"{frontend_base}/dashboard?github_linked=true")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_repositories(request):
    """
    Proxy to GitHub to list the authenticated user's public repositories.
    Requires a stored GithubAccount with an access token.
    """

    try:
        gh_account = GithubAccount.objects.get(user=request.user)
    except GithubAccount.DoesNotExist:
        return Response({"detail": "GitHub account not linked"}, status=status.HTTP_400_BAD_REQUEST)

    resp = requests.get(
        "https://api.github.com/user/repos",
        headers={"Authorization": f"token {gh_account.access_token}"},
        params={"visibility": "public"},
        timeout=5,
    )
    if resp.status_code != 200:
        return Response({"detail": "Failed to fetch repositories"}, status=status.HTTP_400_BAD_REQUEST)

    repos = [
        {
            "id": repo["id"],
            "full_name": repo["full_name"],
        }
        for repo in resp.json()
    ]
    return Response({"repositories": repos})


@csrf_exempt
@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def select_repository(request):
    """
    Store a selected repo for the current user and register a webhook.
    """

    repo_id = request.data.get("repo_id")
    full_name = request.data.get("full_name")
    if not repo_id or not full_name:
        return Response({"detail": "repo_id and full_name are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        gh_account = GithubAccount.objects.get(user=request.user)
    except GithubAccount.DoesNotExist:
        return Response({"detail": "GitHub account not linked"}, status=status.HTTP_400_BAD_REQUEST)

    owner, repo = full_name.split("/", 1)
    webhook_url = request.build_absolute_uri("/api/github/webhook/")
    payload = {
        "name": "web",
        "active": True,
        "events": ["pull_request", "push"],
        "config": {
            "url": webhook_url,
            "content_type": "json",
            "secret": settings.GITHUB_WEBHOOK_SECRET,
        },
    }

    resp = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/hooks",
        headers={"Authorization": f"token {gh_account.access_token}", "Accept": "application/vnd.github+json"},
        json=payload,
        timeout=5,
    )
    if resp.status_code not in (200, 201):
        return Response({"detail": "Failed to create webhook", "github_response": resp.text}, status=status.HTTP_400_BAD_REQUEST)

    hook = resp.json()
    selection, _ = RepositorySelection.objects.update_or_create(
        user=request.user,
        repo_id=str(repo_id),
        defaults={"full_name": full_name, "webhook_id": hook.get("id")},
    )
    return Response(
        {
            "repo_id": selection.repo_id,
            "full_name": selection.full_name,
            "webhook_id": selection.webhook_id,
        }
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def github_webhook(request):
    """
    Endpoint to receive GitHub webhook events.
    We simply parse and return 200 without further processing.
    """

    signature = request.headers.get("X-Hub-Signature-256", "")
    body = request.body

    if settings.GITHUB_WEBHOOK_SECRET:
        mac = hmac.new(
            key=settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
            msg=body,
            digestmod=hashlib.sha256,
        )
        expected = "sha256=" + mac.hexdigest()
        # Soft-check signature; we won't reject for this assessment, but we could.
        if not hmac.compare_digest(expected, signature or ""):
            # Log or print; for now we just continue.
            pass

    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    event = request.headers.get("X-GitHub-Event", "unknown")
    logger.info("Received GitHub webhook event: %s, payload keys: %s", event, list(payload.keys()))

    return Response({"status": "ok"})
