from core.endpoints.basic import index
from core.endpoints.webhooks import (
    github_webhook_endpoint,
    internal_webhook_endpoint,
    zammad_webhook_endpoint,
)
from core.views import days_until, products
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    # Webhooks
    path("webhook/internal/", internal_webhook_endpoint),
    path("webhook/github/", github_webhook_endpoint),
    path("webhook/zammad/", zammad_webhook_endpoint),
    # Public Pages
    path("days-until/", days_until),
    path("products/", products),
]
