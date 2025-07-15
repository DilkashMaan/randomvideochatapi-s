from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
 
    )
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_premium=models.BooleanField(default=False)


class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email} - {self.otp}"
    
class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.reporter.username} reported {self.reported.username}"
   
class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocks_initiated', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocks_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        unique_together = ('blocker', 'blocked')