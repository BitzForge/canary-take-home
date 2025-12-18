from django.urls import path

from . import views

urlpatterns = [
    path("authorize-url/", views.github_authorize_url, name="github-authorize-url"),
    path("callback/", views.github_oauth_callback, name="github-oauth-callback"),
    path("repos/", views.list_repositories, name="github-repos"),
    path("select-repo/", views.select_repository, name="github-select-repo"),
    path("webhook/", views.github_webhook, name="github-webhook"),
]
