from dotenv import load_dotenv
import os
import random
import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer, OTPRequestSerializer, OTPVerifySerializer

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY) 


def generate_otp():
    """Generate 6-digit numeric OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Mock send email - just print OTP to console"""
    print(f"[MOCK EMAIL] Sending OTP to {email}: {otp}")

def generate_jwt(user):
    """Generate JWT token with email claim and 1-hour expiry"""
    payload = {
        "email": user.email,
        "exp": timezone.now() + settings.JWT_EXP_DELTA
    }
    # Use JWT_SECRET from .env
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@api_view(['POST'])
def register(request):
    """Register a new user with email"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']

        # Check if email already registered
        if User.objects.filter(email=email).exists():
            return Response({"message": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        User.objects.create_user(email=email)
        return Response({"message": "Registration successful. Please verify your email."}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def request_otp(request):
    """Generate OTP and print to console"""
    serializer = OTPRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Email not registered."}, status=status.HTTP_400_BAD_REQUEST)

        # Rate limit: allow OTP every 30 seconds
        if user.otp_created_at and (timezone.now() - user.otp_created_at).seconds < 30:
            return Response({"message": "Please wait before requesting a new OTP."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate and save OTP
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Print OTP to terminal (mock email)
        send_otp_email(email, otp)

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_otp(request):
    """Verify OTP and return JWT token"""
    serializer = OTPVerifySerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP must match and not be older than 5 minutes
        if user.otp != otp or (timezone.now() - user.otp_created_at).seconds > 300:
            return Response({"message": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP after successful login
        user.otp = None
        user.save()

        # Generate JWT token
        token = generate_jwt(user)

        return Response({"message": "Login successful.", "token": token}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
