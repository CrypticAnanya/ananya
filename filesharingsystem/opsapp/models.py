from django.db import models
from django.conf import settings

class UploadedFile(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='uploads/ops_files/')
    filename = models.CharField(max_length=512)
    content_type = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} by {self.uploader}"
