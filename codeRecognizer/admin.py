from django.contrib import admin
from django.utils.html import format_html
from .models import CodeFiles

@admin.register(CodeFiles)
class FilesUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'results', 'file', )
    search_fields = ('title', 'generated_docs')
    list_filter = ('uploaded_at',)

    def file(self, obj):
        if obj.code_file:
            # Створюємо красиву кнопку
            return format_html(
                '<a href="{}" target="_blank" style="'
                'padding: 5px 10px; border-radius: 5px; '
                'text-decoration: none; font-weight: bold;">'
                'Відкрити</a>',
                obj.code_file.url
            )
        return "Немає файлу"

    def results(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 10px;">{}</div>',
            obj.generated_docs
        )