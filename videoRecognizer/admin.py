from django.contrib import admin
from django.utils.html import format_html
from .models import VideoUpload
import os

@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'result', 'video_source_type')
    search_fields = ('title', 'result', 'url')
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at', 'video_player')

    def video_source_type(self, obj):
        if obj.video:
            return format_html(
                '<a href="{}" target="_blank" style="color: green; font-weight: bold;">Файл</a>',
                obj.video.url
            )
        elif obj.url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0d6efd; font-weight: bold; text-decoration: underline;">Посилання</a>',
                obj.url
            )
        return "—"

    video_source_type.short_description = "Source"

    def video_player(self, obj):
        if obj.video:
            return format_html(
                '''
                <video controls style="max-width: 100%; max-height: 400px; border-radius: 5px; border: 1px solid #ccc;">
                    <source src="{}" type="video/mp4">
                    Ваш браузер не підтримує відео.
                </video>
                ''',
                obj.video.url
            )

        elif obj.url:
            return format_html(
                '''
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 5px solid #0d6efd;">
                    <p style="margin-bottom: 10px;">Це відео доступне за зовнішнім посиланням:</p>
                    <a href="{}" target="_blank" style="
                        background-color: #0d6efd; color: white; 
                        padding: 8px 15px; border-radius: 5px; 
                        text-decoration: none; font-weight: bold;">
                        ▶ Відкрити відео у новій вкладці
                    </a>
                    <br><br>
                    <small style="color: #666;">URL: {}</small>
                </div>
                ''',
                obj.url, obj.url
            )
        return "Відео відсутнє"

    video_player.short_description = "Перегляд відео"