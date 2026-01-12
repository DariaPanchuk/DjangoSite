from django.db import models

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='images/')
    result = models.CharField(max_length=255, blank=True)
    confidence = models.FloatField(default=0.0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_result_list(self):
        if self.result:
            return self.result.split(', ')
        return []