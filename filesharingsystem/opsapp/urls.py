from django.urls import path
from .views import (
    LoginView, OpsFileUploadView, ClientSignupView, ClientEmailVerifyView,
    ClientListFilesView, ClientRequestDownloadView, FileDownloadView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('ops/upload/', OpsFileUploadView.as_view(), name='ops-upload'),

    path('client/signup/', ClientSignupView.as_view(), name='client-signup'),
    path('client/verify-email/', ClientEmailVerifyView.as_view(), name='client-verify-email'),
    path('client/files/', ClientListFilesView.as_view(), name='client-list-files'),
    path('client/files/<int:file_id>/request-download/', ClientRequestDownloadView.as_view(), name='client-request-download'),
    path('download/', FileDownloadView.as_view(), name='file-download'),
]
