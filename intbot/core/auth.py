from functools import wraps

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter  # type: ignore[import-untyped]
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect


class EuroPythonSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self, request: HttpRequest, sociallogin: object
    ) -> bool:
        email = sociallogin.user.email  # type: ignore[attr-defined]
        return email.endswith("@europython.eu")


def staff_required(view_func):  # type: ignore[no-untyped-def]
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not request.user.is_staff:
            return redirect("/no-access/")
        return view_func(request, *args, **kwargs)

    return login_required(wrapper, login_url="/accounts/login/")
