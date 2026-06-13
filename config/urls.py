"""Top-level URL configuration for the Expense Tracker project."""

from django.contrib import admin
from django.urls import include, path
from . import api_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(api_urls)),
]
