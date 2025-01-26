import hashlib
import hmac
import json

from core.models import Webhook
from core.tasks import process_webhook
from django.conf import settings
from django.http import HttpResponseForbidden
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
            extra={},
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


@csrf_exempt
def github_webhook_endpoint(request):
    if request.method == "POST":
        github_headers = {
            k: v for k, v in request.headers.items() if k.startswith("X-Github")
        }

        try:
            signature = verify_github_signature(request)
        except ValueError as e:
            return HttpResponseForbidden(e)

        wh = Webhook.objects.create(
            source="github",
            meta=github_headers,
            signature=signature,
            content=json.loads(request.body),
            extra={},
        )
        process_webhook.enqueue(str(wh.uuid))
        return JsonResponse({"status": "ok"})

    return HttpResponseNotAllowed("Only POST")


def verify_github_signature(request) -> str:
    """Verify that the payload was sent by github"""

    if "X-Hub-Signature-256" not in request.headers:
        raise ValueError("X-Hub-Signature-256 is missing")

    signature = request.headers["X-Hub-Signature-256"]

    hashed = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET_TOKEN.encode("utf-8"),
        msg=request.body,
        digestmod=hashlib.sha256,
    )

    expected = "sha256=" + hashed.hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise ValueError("Signature's don't match")

    return signature
