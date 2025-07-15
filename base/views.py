from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# from .models import User
from django.contrib.auth.models import User
from .serializer import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializer import ProfileUpdateSerializer
from .matchmaker import add_to_queue, pop_match, remove_from_queue
from .zego import generate_token, ZEGOCLOUD_APP_ID
import stripe
from .models import Report,Block
from django.conf import settings
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail as django_send_mail
from django.conf import settings
import random
from .models import EmailOTP
from django.utils import timezone
from datetime import timedelta

#Email Configuration
@api_view(['POST'])
@permission_classes([AllowAny])
def send_mail(request):
    context = {}
    email = request.data.get('email')
    otp = str(random.randint(100000, 999999))
    subject = "Verify your email"
    message = "Your OTP is: " + otp
 
    if email:
        try:
            # Save OTP to DB
            EmailOTP.objects.create(email=email, otp=otp)
 
            # Send OTP via email
            django_send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            context['result'] = 'Email sent successfully'
        except Exception as e:
            context['result'] = f'Error sending email: {e}'
    else:
        context['result'] = 'Email field is required'
 
    return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)
 
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
 
    try:
        otp_entry = EmailOTP.objects.filter(email=email, otp=otp).latest('created_at')
       
        if timezone.now() > otp_entry.created_at + timedelta(minutes=5):
            return Response({'detail': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            user.profile.is_verified = True
            user.profile.save()
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
 
        return Response({'detail': 'OTP verified successfully'}, status=status.HTTP_200_OK)
 
    except EmailOTP.DoesNotExist:
        return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)




stripe.api_key = 'sk_test_51RGxNjQrJsZ6OOXJKkKOCl0hrx8x9XwzCxfBvwajVtFrJSMfhWp71h7EFYDIgAdXpiNDKeacXYv0prWS5R6iLZXM008yvKbrh7'
@api_view(['GET'])
@permission_classes([AllowAny])
def get_plans(request):
    try:
        products = stripe.Product.list(active=True, expand=['data.default_price'])
 
        plans = []
        for product in products.data:
            price = product.get('default_price')
            plans.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'image': product.images[0] if product.images else '',
                'price_id': price.id if price else '',
                'amount': price.unit_amount if price else 0,
                'interval': price.recurring.interval if price and price.recurring else '',
                'currency': price.currency if price else 'usd',
            })
 
        return Response(plans)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def create_checkout_session(request):
    try:
        price_id = request.data.get("price_id")

        if not price_id:
            return Response({"error": "Price ID is required"}, status=400)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url="https://python-backend-ez1r.onrender.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://python-backend-ez1r.onrender.com/cancel",
        )

        return Response({"sessionId": checkout_session.id})
    except Exception as e:
        return Response({"error": str(e)}, status=500)







@api_view(['POST'])
def join_call(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id required'}, status=400)
 
    add_to_queue(user_id)
 
    # Try to match with another waiting user
    u1, u2 = pop_match()
    if u1 and u2:
        room_id = f"room_{u1}_{u2}"
        return Response({
            'matched': True,
            'room_id': room_id,
            'self_token': generate_token(u1),
            'partner_token': generate_token(u2),
            'app_id': ZEGOCLOUD_APP_ID,
            'self_id': u1,
            'partner_id': u2
        })
 
    return Response({'matched': False, 'message': 'Waiting for a partner...'})



 
@api_view(['GET'])
def check_auth(request):
    return Response({'authenticated': True, 'user': request.user.username,'user_id': request.user.id})

@api_view(['GET'])
def get_user(request):
    users = User.objects.all()
    serializer= UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_userbyid(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
 
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def gender_count(request):
    counts = UserProfile.objects.values('gender').annotate(total=Count('gender'))
    gender_data = {entry['gender']: entry['total'] for entry in counts}

    for gender in ['male', 'female']:
        gender_data.setdefault(gender, 0)

    return Response(gender_data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProfileUpdateSerializer(
        instance={'user': user, 'profile': profile},
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profile updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_photo(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    if profile.profile_photo:
        profile.profile_photo.delete(save=False)  
        profile.profile_photo = None
        profile.save()
 
    return Response({'message': 'Profile photo deleted successfully'}, status=status.HTTP_200_OK)
 



@api_view(['PUT', 'DELETE'])
def update_user(request, pk):
    try:
        user=User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer=UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    identifier = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    user = authenticate(username=identifier, password=password)
    if user is None:
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.profile.is_verified:
        return Response({'error': 'Email not verified. Please verify your account.'}, status=403)
    refresh = RefreshToken.for_user(user)
    response = Response({"message": "Login successful", "user_id": user.id,"email": user.email,"gender": user.profile.gender,"is_verified": user.profile.is_verified,"is_premium":user.profile.is_premium})
    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,
        secure=True,       # Required for cross-site cookies
        samesite='None',   # Allows cross-origin
        max_age=86400,     # 1 day
    )
    response.set_cookie(
        key='user_id',
        value=str(user.id),
        httponly=True,    # Allow JS access if needed
        secure=True,
        samesite='Lax',
        max_age=86400,
    )
    response.set_cookie(
        key='gender',
        value=str(user.profile.gender),
        httponly=True,    # Allow JS access if needed
        secure=False,
        samesite='Lax',
        max_age=86400,
    )
    return response
 
 
@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    response = Response({"message": "Logged out successfully"})
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('user_id', path='/')
    response.delete_cookie('gender', path='/')
    response.delete_cookie('sessionid')
 
    return response
 
# Report User
 
@api_view(['POST'])
def report(request):
    user_reporter_id = request.data.get('user_reporter')
    user_reported_id = request.data.get('user_reported')
    reason = request.data.get('reason')
    if not user_reporter_id or not user_reported_id:
        return Response({'error': 'Both reporter and reported user IDs are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if user_reporter_id == user_reported_id:
        return Response({'error': 'Users cannot report themselves.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        reporter = User.objects.get(id=user_reporter_id)
        reported = User.objects.get(id=user_reported_id)
    except User.DoesNotExist:
        return Response({'error': 'Invalid user ID(s) provided.'}, status=status.HTTP_404_NOT_FOUND)
    Report.objects.create(reporter=reporter, reported=reported, reason=reason)
    return Response({'message': 'Report submitted successfully.'}, status=status.HTTP_201_CREATED)

#Block User
@api_view(['POST'])
def block(request):
    blocker= request.data.get('blocker')
    blocked= request.data.get('blocked')
    if not blocker or not blocked:
        return Response({'error': 'Both blocker and blocked user IDs are required.'}, status=status.HTTP_400_BAD_REQUEST)
 
    if blocker == blocked:
        return Response({'error': 'Users cannot block themselves.'}, status=status.HTTP_400_BAD_REQUEST)
 
    try:
        blocker = User.objects.get(id=blocker)
        blocked = User.objects.get(id=blocked)
    except User.DoesNotExist:
        return Response({'error': 'One or both users not found.'}, status=status.HTTP_404_NOT_FOUND)
 
    if Block.objects.filter(blocker=blocker, blocked=blocked).exists():
        return Response({'error': 'User is already blocked.'}, status=status.HTTP_409_CONFLICT)
 
    Block.objects.create(blocker=blocker, blocked=blocked)
 
    return Response({'message': 'User blocked successfully.'}, status=status.HTTP_201_CREATED)


#User  Count

@api_view(['GET'])
def get_user_count(request):
    user_count = User.objects.count()
    return Response({'user_count': user_count}, status=status.HTTP_200_OK)

#Resend OTP
 
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    otp = str(random.randint(100000, 999999))
    subject = "Resend OTP - Verify your email"
    message = "Your new OTP is: " + otp
    try:
        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email, otp=otp)
        django_send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return Response({'detail': 'OTP resent successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': f'Error resending OTP: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 