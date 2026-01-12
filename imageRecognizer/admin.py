from django.contrib import admin
from .models import ImageUpload

@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at', 'result', 'confidence', 'image')
    readonly_fields = ('uploaded_at',)
    list_filter = ('uploaded_at',)