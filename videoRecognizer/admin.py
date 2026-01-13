from django.contrib import admin
from .models import VideoUpload

@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_at', 'result')
    search_fields = ('title', 'result', 'url')
    list_filter = ('uploaded_at',)

    def short_result(self, obj):
        if obj.result:
            return obj.result[:50] + "..."
        return "-"

    short_result.short_description = "Результат аналізу"