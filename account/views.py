from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from .permissions import IsParentOrAdmin


class TelegramRegisterView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail":"user created succeful"})
    
class ActivateView(APIView):
    authentication_classes = []

    def get(self, request):
        activation_code = request.query_params.get('u')
        user = get_object_or_404(CustomUser, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response({"detail":"account activated"})
    
class MyTokenObtainPairView(TokenObtainPairView):
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
        





