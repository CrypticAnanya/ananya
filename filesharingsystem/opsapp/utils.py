from django.core import signing
from django.conf import settings

SIGNING_SALT = 'file-download-salt'  # change to project-specific secret
DOWNLOAD_TOKEN_MAX_AGE = 60 * 10  # 10 minutes

def make_download_token(file_id, client_id):
    payload = {'file_id': file_id, 'client_id': client_id}
    token = signing.dumps(payload, salt=SIGNING_SALT)
    return token

def verify_download_token(token, max_age=DOWNLOAD_TOKEN_MAX_AGE):
    try:
        payload = signing.loads(token, salt=SIGNING_SALT, max_age=max_age)
        return payload  # dict with file_id and client_id
    except signing.BadSignature:
        return None
    except signing.SignatureExpired:
        return None
