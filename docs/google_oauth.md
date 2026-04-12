# Google OAuth Login

Users log in with their `@europython.eu` Google Workspace accounts via [django-allauth](https://docs.allauth.org/).

Only `@europython.eu` emails are allowed — other domains see a friendly error page. On first login a Django user is created with `is_staff=False`, so they can log in but can't access protected pages until an admin promotes them in Django admin.

Protected views use a `@staff_required` decorator (`core/auth.py`) that checks both authentication and staff status.

## Setup

### Production

1. In [Google Cloud Console](https://console.cloud.google.com/), create an OAuth client ID (Web application) with redirect URI:
   ```
   https://internal.europython.eu/accounts/google/login/callback/
   ```
2. Set env vars on the server:
   ```
   GOOGLE_OAUTH_CLIENT_ID=<your-client-id>
   GOOGLE_OAUTH_CLIENT_SECRET=<your-client-secret>
   ```
3. Deploy and run migrations (`make deploy/app` handles this)

### Local development

Create a separate OAuth client with redirect URI `http://localhost:4672/accounts/google/login/callback/` and add credentials to `intbot/.env`. Then run `make migrate`.

You can also skip this entirely — create users via Django admin and use `force_login()` in tests.

## Granting access to users

1. Go to Django admin (`/admin/` > **Users**)
2. Find the user and set **Staff status** to checked
3. Save — the user can now access protected pages

## Files

- `core/auth.py` — `EuroPythonSocialAccountAdapter` (domain restriction) and `staff_required` decorator
- `templates/account/login.html` — login page with Google button
- `templates/no_access.html` — shown to logged-in non-staff users
- `templates/socialaccount/authentication_error.html` — shown for non-europython.eu emails

## Settings

Allauth config in `intbot/settings.py`:

- `SOCIALACCOUNT_ONLY = True` — only social login, no username/password
- `ACCOUNT_EMAIL_VERIFICATION = "none"` — Google already verifies emails
- `SOCIALACCOUNT_ADAPTER` — points to our adapter that restricts to `@europython.eu`
- Google credentials configured via env vars, no `SocialApp` database entries needed
