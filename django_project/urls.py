"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def healthcheck(request):
    return HttpResponse("ok")

def debug_db(request):
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        count = User.objects.count()
        return HttpResponse(f"DB Connection OK. User count: {count}")
    except Exception as e:
        return HttpResponse(f"DB Connection FAILED: {str(e)}", status=500)

urlpatterns = [
    path("health/", healthcheck, name="healthcheck"),
    path("debug-db/", debug_db, name="debug_db"),
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("pages.urls")),
    path("hotels/", include("hotels.urls")),
    path("rooms/", include("rooms.urls")),
    path("bookings/", include("bookings.urls")),
    path("payments/", include("payments.urls")),
    path("reviews/", include("reviews.urls")),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
