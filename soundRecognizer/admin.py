from django.contrib import admin
from .models import AudioUpload

@admin.register(AudioUpload)
class AudioUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_at', 'result')
    search_fields = ('title', 'result')
    list_filter = ('uploaded_at',)