from core.endpoints.basic import index
from core.endpoints.webhooks import github_webhook_endpoint, internal_webhook_endpoint
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    # Internal Webhooks
    path("webhook/internal/", internal_webhook_endpoint),
    path("webhook/github/", github_webhook_endpoint),
]
