from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
 
 
class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    profile_photo = serializers.ImageField(required=False)  
 
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password','is_active','gender','dob','profile_photo']
        extra_kwargs = {'password': {'write_only': True}}
   
    def validate_gender(self, value):
        valid_genders = ['male', 'female', 'other']
        if value.lower() not in valid_genders:
            raise serializers.ValidationError("Gender must be 'male', 'female', or 'other'")
        return value.lower()
 
 
    def create(self, validated_data):
        gender = validated_data.pop('gender', None)
        dob = validated_data.pop('dob', None)
        profile_photo = validated_data.pop('profile_photo', None)
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        UserProfile.objects.create(user=user, gender=gender, dob=dob, profile_photo=profile_photo)
 
        return user
 
    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['gender'] = instance.profile.gender
            data['dob'] = instance.profile.dob
            data['profile_photo'] = instance.profile.profile_photo.url if instance.profile.profile_photo else None
            data['is_verified'] = instance.profile.is_verified
            data['is_premium'] = instance.profile.is_premium
        except UserProfile.DoesNotExist:
            data['gender'] = None
            data['dob'] = None
            data['profile_photo'] = None
            data['is_premium'] = None
            data['is_verified'] = None
 
        return data
   
 
 
 
class ProfileUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    profile_photo = serializers.ImageField(required=False)
 
    def update(self, instance, validated_data):
        user = instance['user']
        profile = instance['profile']
        if 'username' in validated_data:
            user.username = validated_data.get('username', user.username)
        user.save()
        if 'profile_photo' in validated_data:
            profile.profile_photo = validated_data.get('profile_photo', profile.profile_photo)
        profile.save()
 
        return instance