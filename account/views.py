from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
#
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
#
from .models import  User
from .serializers import UserSerializer
from .auth import TelegramAuthentication
from .permissions import IsParentOrAdmin,IsParentOfChild,IsAdmin


class TelegramRegisterView(APIView):
    authentication_classes = []
#тут просто чтоб было красиво в свагере с описанием на запрос сразу понять
    @swagger_auto_schema(
        operation_summary="Регистрация пользователя через Telegram",
        request_body=UserSerializer,
        responses={201: "Пользователь успешно создан", 400: "Ошибка валидации данных"},
    )


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail":"user created succeful"})
    

class TelegramLoginView(APIView):
    authentication_classes = [TelegramAuthentication]
    #описание
    @swagger_auto_schema(
        operation_summary="Логин через Telegram ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['telegram_id'],
            properties={
                'telegram_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Telegram ID пользователя'),
            }
        ),
        responses={200: UserSerializer}
    )

    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        user = get_object_or_404(User, telegram_id=telegram_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)


class ChildRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsParentOrAdmin]


class CheckRoleView(APIView):
    authentication_classes = [TelegramAuthentication]
    
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        user = get_object_or_404(User, telegram_id=telegram_id)
        return Response({'role':user.role})
    
class GetChildsView(APIView):
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsParentOfChild]
    #
    @swagger_auto_schema(
        operation_summary="Получить список детей пользователя",
        manual_parameters=[
            openapi.Parameter(
                'user_id', openapi.IN_QUERY, description="ID родителя", type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: UserSerializer(many=True)}
    )

    def get(self, request):
        user_id = request.query_params.get('user_id')
        parent = User.objects.get(id=user_id)

        self.check_object_permissions(request,parent)#обязвтельный - родитель имеет права видеть только своего ребенка 

        children = parent.children.all()
        serializer = UserSerializer(children, many=True)
        return Response(serializer.data)
    
class GetUserView(APIView):
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        phone = request.query_params.get('phone')
        user = get_object_or_404(User, phone=phone)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)
        





