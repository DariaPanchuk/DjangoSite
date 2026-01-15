from django.contrib import admin
from django.utils.html import format_html
from .models import ImageUpload

@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ('image', 'uploaded_at', 'result', 'confidence', 'file')
    search_fields = ('uploaded_at', 'result', 'confidence', 'image')
    list_filter = ('uploaded_at',)

    def file(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 200px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "Немає фото"