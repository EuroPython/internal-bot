import hmac
import json

from core.models import Webhook
from core.tasks import process_webhook
from django.conf import settings
from django.http.response import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def internal_webhook_endpoint(request):
    if request.method == "POST":
        try:
            verify_internal_webhook(request)
        except ValueError as e:
            return JsonResponse({"status": "bad", "message": str(e)}, status=403)

        wh = Webhook.objects.create(
            source="internal",
            content=json.loads(request.body),
        )
        process_webhook.enqueue(str(wh.uuid))

        return JsonResponse({"status": "created", "guid": wh.uuid})

    return HttpResponseNotAllowed("Only POST")


def verify_internal_webhook(request):
    """raise ValueError if incorrect token"""

    if "Authorization" not in request.headers:
        raise ValueError("Authorization token is missing")

    token = request.headers["Authorization"]

    if not hmac.compare_digest(settings.WEBHOOK_INTERNAL_TOKEN, token):
        raise ValueError("Token doesn't match")
