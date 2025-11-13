from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h3>File Sharing API</h3><p>Use /api/ for endpoints</p>")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('opsapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
