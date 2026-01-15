from django.db import models

class CodeFiles(models.Model):
    code_file = models.FileField(upload_to='source_code/')
    title = models.CharField(max_length=255, blank=True)
    generated_docs = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or "Code File"