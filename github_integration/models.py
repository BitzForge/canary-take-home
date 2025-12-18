from django.conf import settings
from django.db import models


class GithubAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="github_account",
    )
    access_token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=50, default="bearer")
    scope = models.CharField(max_length=255, blank=True)
    github_user_id = models.CharField(max_length=255)
    github_username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.github_username


class RepositorySelection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="selected_repositories",
    )
    repo_id = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)  # e.g. owner/repo
    webhook_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "repo_id")

    def __str__(self) -> str:
        return f"{self.user} -> {self.full_name}"

