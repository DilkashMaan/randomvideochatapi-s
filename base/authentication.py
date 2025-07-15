from rest_framework_simplejwt.authentication import JWTAuthentication
 
class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Try to get the token from 'Authorization' header (default behavior)
        header_auth = super().authenticate(request)
        if header_auth is not None:
            return header_auth
 
        # Fallback: Try to get token from cookie
        token = request.COOKIES.get('access_token')
        if token is None:
            return None
       
        # Use JWTAuthentication's token validation
        validated_token = self.get_validated_token(token)
        return self.get_user(validated_token), validated_token