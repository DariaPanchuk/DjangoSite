from django.contrib import admin
from django.utils.html import format_html
from .models import SpectrumAudio

@admin.register(SpectrumAudio)
class AudioUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_at', 'result_text', 'audio_player')
    search_fields = ('title', 'result_text')
    list_filter = ('uploaded_at',)

    def audio_player(self, obj):
        if obj.audio:
            return format_html(
                '<audio controls style="width: 200px; height: 30px;">'
                '<source src="{}" type="audio/mpeg">'
                'Ваш браузер не підтримує аудіо.'
                '</audio>',
                obj.audio.url
            )
        return "Немає аудіо"

    audio_player.short_description = "Прослухати"