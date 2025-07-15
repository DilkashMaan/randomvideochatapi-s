from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
 
class ClearExpiredTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
 
    def __call__(self, request):
        token = request.COOKIES.get('access_token')
 
        # Always call the view and get the response first
        response = self.get_response(request)
 
        if token:
            try:
                AccessToken(token)  # Will raise if expired or invalid
            except (TokenError, InvalidToken):
                # Delete all relevant cookies
                response.delete_cookie('access_token')
                response.delete_cookie('user_id')
                response.delete_cookie('gender')
 
        return response