from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)



from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('apps.account.urls')),
    path('document/',include('apps.document.urls')),
    path('agent/',include('apps.agent.urls')),
    path('briefings/',include('apps.nightly_brain.urls')),
    path("health/", health_check, name="health_check"),
]
