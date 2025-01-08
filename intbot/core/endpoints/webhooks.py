import json
from django.http.response import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.models import Webhook

@csrf_exempt
def internal_webhook_endpoint(request):
    if request.method == "POST":
        print(request.body)
        wh = Webhook.objects.create(
            source="internal",
            content=json.loads(request.body),
        )

        return JsonResponse({"status": "created", "guid": wh.uuid})

    return HttpResponseNotAllowed("Only POST")
