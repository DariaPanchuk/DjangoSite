from django.db import models

class SpectrumAudio(models.Model):
    audio = models.FileField(upload_to='spectrum_audio/')
    title = models.CharField(max_length=255, blank=True)
    result_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_result_list(self):
        if self.result_text:
            return self.result_text.split(', ')
        return []

    def __str__(self):
        return f"Signal {self.id}"