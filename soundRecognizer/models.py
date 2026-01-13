from django.db import models

class AudioUpload(models.Model):
    audio = models.FileField(upload_to='audio/')
    title = models.CharField(max_length=255, blank=True)
    result = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_result_list(self):
        if self.result:
            return self.result.split(', ')
        return []

    def __str__(self):
        return f"Audio {self.id}"