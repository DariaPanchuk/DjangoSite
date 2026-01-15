from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('spectrumRecognizer/', include('spectrumRecognizer.urls')),
    path('soundRecognizer/', include('soundRecognizer.urls')),
    path('videoRecognizer/', include('videoRecognizer.urls')),
    path('imageRecognizer/', include("imageRecognizer.urls")),
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)