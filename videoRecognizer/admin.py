from django.contrib import admin
from .models import VideoUpload

@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_at', 'result')
    search_fields = ('title', 'result', 'url')
    list_filter = ('uploaded_at',)