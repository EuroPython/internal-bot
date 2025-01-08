from django.http.response import JsonResponse
from django.conf import settings


def index(request):
    return JsonResponse(
        {
            "hello": "world",
            "v": settings.APP_VERSION,
        }
    )
