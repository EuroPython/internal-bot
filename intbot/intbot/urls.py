from django.contrib import admin
from django.urls import path

from core.endpoints.basic import index
from core.endpoints.webhooks import internal_webhook_endpoint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    # Internal Webhooks
    path('webhook/internal/', internal_webhook_endpoint),
]
