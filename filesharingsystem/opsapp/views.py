from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .serializers import FileUploadSerializer, ClientSignupSerializer
from .models import UploadedFile
from .permissions import IsOpsUser, IsClientUser
from .utils import make_download_token, verify_download_token

# 1) Login (shared endpoint - returns token)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"detail":"username and password required"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request=request, username=username, password=password)
        if not user:
            return Response({"detail":"invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.id, "username": user.username})

# 2) Ops upload (only ops)
class OpsFileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOpsUser]
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                "id": instance.id,
                "filename": instance.filename,
                "uploaded_at": instance.uploaded_at,
                "size": instance.size,
                "content_type": instance.content_type,
                "download_url": request.build_absolute_uri(instance.file.url),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3) Client signup (returns encrypted/signed URL for verification)
class ClientSignupView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = ClientSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # add to client group
            group, _ = Group.objects.get_or_create(name='client')
            user.groups.add(group)
            user.save()

            # create verification token (signed payload)
            from django.core import signing
            payload = {'user_id': user.id}
            token = signing.dumps(payload, salt='email-verify-salt')

            verify_path = reverse('client-verify-email')  # we'll add this URL
            verify_url = request.build_absolute_uri(f"{verify_path}?token={token}")

            # send verification email (console backend prints it)
            send_mail(
                subject="Verify your email",
                message=f"Click to verify your email: {verify_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

            # Return the verification URL as response (encrypted/signed)
            return Response({"detail":"Signup successful. Verification email sent.", "verification_url": verify_url}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Email verification endpoint
class ClientEmailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return Response({"detail":"token required"}, status=status.HTTP_400_BAD_REQUEST)
        from django.core import signing
        try:
            payload = signing.loads(token, salt='email-verify-salt', max_age=60*60*24)  # 1 day
        except Exception:
            return Response({"detail":"invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = payload.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save()
        return Response({"detail":"email verified, you can login now."})

# 4) Client: list all uploaded files
class ClientListFilesView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]
    def get(self, request):
        files = UploadedFile.objects.all().order_by('-uploaded_at')
        data = [{
            "id": f.id, "filename": f.filename, "uploaded_at": f.uploaded_at,
            "size": f.size, "uploader": f.uploader.username
        } for f in files]
        return Response(data)

# 5) Client: request download => returns signed download URL (token)
class ClientRequestDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]
    def post(self, request, file_id):
        # file_id from URL
        file = get_object_or_404(UploadedFile, id=file_id)
        client_id = request.user.id
        token = make_download_token(file_id=file.id, client_id=client_id)
        # build download endpoint URL
        download_path = reverse('file-download')  # we'll add in urls
        download_url = request.build_absolute_uri(f"{download_path}?token={token}")
        return Response({"download_url": download_url, "expires_in_seconds": 600})

# 6) Download endpoint (validates token + user)
from django.http import FileResponse, HttpResponseForbidden, Http404
class FileDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return Response({"detail":"token required"}, status=status.HTTP_400_BAD_REQUEST)
        payload = verify_download_token(token)
        if not payload:
            return Response({"detail":"invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        file_id = payload.get('file_id')
        client_id = payload.get('client_id')
        # ensure the requester is the same client
        if request.user.id != client_id:
            return HttpResponseForbidden("You are not allowed to download this file.")
        uploaded = get_object_or_404(UploadedFile, id=file_id)
        # return file response
        try:
            response = FileResponse(uploaded.file.open('rb'), as_attachment=True, filename=uploaded.filename)
            return response
        except FileNotFoundError:
            raise Http404("File not found.")
