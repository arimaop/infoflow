from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST


def _no_store_response(response):
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response["Vary"] = "Cookie"
    return response


@never_cache
@require_http_methods(["GET", "POST"])
def admin_logout_view(request):
    logout(request)
    request.session.flush()
    return _no_store_response(redirect("/"))


@never_cache
@require_POST
def clear_admin_log_view(request):
    count, _ = LogEntry.objects.filter(user=request.user).delete()
    messages.success(
        request,
        f"История последних действий очищена ({count} записей).",
    )
    response = redirect("admin:index")
    response["Clear-Site-Data"] = '"cache"'
    return _no_store_response(response)


def register_admin_auth_urls():
    original_get_urls = admin.site.get_urls

    def get_urls():
        custom_urls = [
            path(
                "clear-log/",
                admin.site.admin_view(clear_admin_log_view),
                name="clear_log",
            ),
        ]
        return custom_urls + original_get_urls()

    admin.site.get_urls = get_urls
