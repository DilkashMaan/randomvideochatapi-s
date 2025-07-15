from django.urls import path
from .views import  get_user,create_user,update_user,login,check_auth,logout,update_profile,get_userbyid,delete_profile_photo,join_call,get_plans,create_checkout_session,gender_count,send_mail,verify_otp,get_user_count,report,block,resend_otp
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns=[

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('users/', get_user, name='get_user'),
    path('users/signup/', create_user, name='create_user'),
    path('auth/check/',check_auth, name='check_auth'),
    path('users/logout/',logout,name='logout'),
    path('users/<int:pk>/',update_user, name='update_user'),
    path('login/',login, name='login'),
    path('update_profile/', update_profile, name='update_profile'),
    path('user/<int:user_id>/', get_userbyid, name='get_userbyid'),
    path('delete_pf/', delete_profile_photo, name='delete_profile_photo'),
    path('join_call/', join_call, name='join_call'),
    path('plans/', get_plans, name='get_plans'),
    path('subscribe/', create_checkout_session, name='create_checkout_session'),
    path('gender/', gender_count, name='gender_count'),
    path('send_mail/', send_mail, name='send_mail'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('user_count/', get_user_count, name='get_user_count'),
    path('report/', report, name='report'),
    path('block/', block, name='block'),
    path('resend_otp/', resend_otp, name='resend_otp'),


]
