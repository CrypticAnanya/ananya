from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'uploader', 'size', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
