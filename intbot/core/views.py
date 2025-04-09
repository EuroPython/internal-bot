from django.conf import settings
from django.template.response import TemplateResponse
from django.utils import timezone


def days_until(request):
    delta = settings.CONFERENCE_START - timezone.now()

    return TemplateResponse(request, "days_until.html", {"days_until": delta.days})
