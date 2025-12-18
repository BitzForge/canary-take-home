from django.urls import path

from . import views

urlpatterns = [
    path("auth/google/", views.google_login, name="google-login"),
]


