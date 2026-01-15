from django.contrib import admin
from django.utils.html import format_html
from .models import AudioUpload

@admin.register(AudioUpload)
class AudioUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'result', 'player')
    search_fields = ('title', 'result')
    list_filter = ('uploaded_at',)

    def player(self, obj):
        if obj.audio:
            return format_html(
                '<audio controls style="width: 200px; height: 30px;">'
                '<source src="{}" type="audio/mpeg">'
                'Ваш браузер не підтримує аудіо.'
                '</audio>',
                obj.audio.url
            )
        return "Немає аудіо"