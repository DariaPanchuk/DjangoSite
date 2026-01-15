from django.db import models
import os

class VideoUpload(models.Model):
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    result = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.video and not self.title:
            self.title = os.path.basename(self.video.name)

        elif self.url and not self.title:
            self.title = "YouTube Video"

        super().save(*args, **kwargs)

    def get_result_list(self):
        if self.result:
            return self.result.split(', ')
        return []

    def __str__(self):
        return self.title if self.title else f"Video {self.id}"