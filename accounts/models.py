from django.conf import settings
from django.db import models


class AppUser(models.Model):
    """
    Simple user model tied to a Google account.
    We avoid replacing Django's auth user for this assessment.
    """

    django_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="app_profile"
    )
    google_sub = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.email

