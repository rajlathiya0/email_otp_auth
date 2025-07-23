from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register),
    path('request-otp', views.request_otp),
    path('verify-otp', views.verify_otp),
]
