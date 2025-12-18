import logging

import requests
from django.contrib.auth import get_user_model, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import AppUser

logger = logging.getLogger(__name__)

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@csrf_exempt
@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
def google_login(request):
    """
    Accepts a Google access token from the frontend, verifies it with Google,
    and creates/logs in a Django user. Returns a simple user payload.
    """
    access_token = request.data.get("access_token")
    if not access_token:
        return Response(
            {"detail": "access_token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        resp = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5,
        )
    except requests.RequestException:
        logger.exception("Failed to reach Google userinfo endpoint")
        return Response({"detail": "Could not verify token"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if resp.status_code != 200:
        return Response({"detail": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

    payload = resp.json()
    sub = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name", "")

    if not email or not sub:
        return Response({"detail": "Missing email or sub from Google"}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    user, _ = User.objects.get_or_create(username=email, defaults={"email": email})

    AppUser.objects.update_or_create(
        django_user=user,
        defaults={"google_sub": sub, "email": email, "full_name": name},
    )

    auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    return Response({"id": user.id, "email": email, "name": name})
