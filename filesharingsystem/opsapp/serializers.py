from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UploadedFile

ALLOWED_EXTENSIONS = ('.pptx', '.docx', '.xlsx')
ALLOWED_MIME_TYPES = {
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    class Meta:
        model = UploadedFile
        fields = ('id','file','filename','content_type','size','uploaded_at')
        read_only_fields = ('id','filename','content_type','size','uploaded_at')

    def validate_file(self, uploaded_file):
        name = uploaded_file.name.lower()
        if not any(name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise serializers.ValidationError("Invalid file extension. Only .pptx, .docx, .xlsx allowed.")
        # optional mime check
        content_type = getattr(uploaded_file, 'content_type', None)
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError("Invalid MIME type.")
        return uploaded_file

    def create(self, validated_data):
        f = validated_data['file']
        instance = UploadedFile.objects.create(
            uploader=self.context['request'].user,
            file=f,
            filename=f.name,
            content_type=getattr(f, 'content_type', ''),
            size=f.size,
        )
        return instance

class ClientSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('username','email','password','first_name','last_name')

    def create(self, validated_data):
        pw = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(pw)
        user.is_active = False   # require email verification
        user.save()
        # add to client group (done in view)
        return user
