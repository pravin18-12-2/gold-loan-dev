import uuid

class AuthService:
    def login(self):
        return {
            'access_token': f'token-{uuid.uuid4()}',
            'refresh_token': f'refresh-{uuid.uuid4()}',
            'role': 'APPRAISER',
            'expires_in': 3600,
        }

    def face_verify(self):
        return {'verified': True, 'confidence': 0.94}
