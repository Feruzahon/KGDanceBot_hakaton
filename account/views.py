from django.shortcuts import render, get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from .permissions import IsParentOrAdmin

from decouple import config


class TelegramRegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail":"user created succeful"})
    
class ActivateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        activation_code = request.query_params.get('u')
        user = get_object_or_404(CustomUser, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response({"detail":"account activated"})
    
HOST = config('HOST_FOR_SEND_MAIL')
class PasswordResetAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(CustomUser, email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        code = get_random_string(8)
        message=''
        html = f"Код для подтверждения: <b>{code}<b/>"
        send_mail(
            subject = 'Восстановление пароля',
            message=message,
            from_email='abdrahmanovtemirlan71@gmail.com',
            html_message=html,
            recipient_list=[email],
        )
        return Response({"uid":uid, "token":token, "code":code}, status=200)
    
class PasswordResetConfirmAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, uidb64, token):
        password = request.data.get('new_password')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except Exception:
            return Response({"detail":"Invalid uid"}, status=400)
        
        if not PasswordResetTokenGenerator().check_token(user,token):
            return Response({"detail": "Bad or expired token"}, status=400)
        user.set_password(password)
        user.save()
        return Response({"detail": "Password changed"},status=200)

class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = []
    serializer_class = MyTokenObtainPairSerializer

class ChildRegisterView(APIView):
    permission_classes = [IsParentOrAdmin]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail":"child created succesful"})

class CheckRoleView(APIView):
    def get(self, request):
        return Response({'role':request.user.role})
    
class GetChildsView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        parent = CustomUser.objects.get(id=user_id)
        children = parent.children.all()
        serializer = UserSerializer(children, many=True)
        return Response(serializer.data)
    
class GetUserView(APIView):
    def get(self, request):
        phone = request.query_params.get('phone')
        user = get_object_or_404(CustomUser, phone=phone)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)
        





