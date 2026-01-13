from django.db import models

class VideoUpload(models.Model):
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    result = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    def get_result_list(self):
        if self.result:
            return self.result.split(', ')
        return []

    def __str__(self):
        return f"Video {self.id} ({self.uploaded_at})"