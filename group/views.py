"""from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import ProtectedError

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Group
from .serializers import GroupSerializer
from account.models import User
from account.serializers import UserSerializer
from account.permissions import IsAdmin
from account.auth import TelegramAuthentication


class GroupViewSet(ViewSet):
    authentication_classes = [TelegramAuthentication]

    # 1) Список всех групп
    @swagger_auto_schema(
        operation_summary="Список всех групп",
        tags=["Group"],
        responses={200: GroupSerializer(many=True)}
    )
    def list(self, request):
        groups = Group.objects.all().order_by('time')
        return Response(GroupSerializer(groups, many=True).data)

    # 2) Создать группу
    @swagger_auto_schema(
        operation_summary="Создать новую группу (только админ)",
        tags=["Group"],
        request_body=GroupSerializer,
        responses={201: GroupSerializer}
    )
    def create(self, request):
        if not request.user.is_admin:
            return Response({"detail": "Нет прав"}, status=403)
        serializer = GroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    # 3) Получить одну группу
    @swagger_auto_schema(
        operation_summary="Получить информацию о группе",
        tags=["Group"],
        responses={200: GroupSerializer}
    )
    def retrieve(self, request, pk=None):
        group = Group.objects.get(id=pk)
        return Response(GroupSerializer(group).data)

    # 4) Обновить группу
    @swagger_auto_schema(
        operation_summary="Обновить группу (только админ)",
        tags=["Group"],
        request_body=GroupSerializer,
        responses={200: GroupSerializer}
    )
    def update(self, request, pk=None):
        if not request.user.is_admin:
            return Response({"detail": "Нет прав"}, status=403)

        group = Group.objects.get(id=pk)
        serializer = GroupSerializer(group, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # 5) Удалить группу
    @swagger_auto_schema(
        operation_summary="Удалить группу",
        tags=["Group"],
        responses={200: "Группа удалена", 400: "Ошибка"}
    )
    def destroy(self, request, pk=None):
        try:
            Group.objects.get(id=pk).delete()
            return Response({"detail": "Группа удалена"})
        except ProtectedError:
            return Response({"detail": "Активные абонементы — удаление запрещено"}, status=400)


from rest_framework.decorators import action

class GroupViewSet(ViewSet):
    ...
    
    @action(detail=True, methods=['patch'], url_path='add-user')
    @swagger_auto_schema(
        operation_summary="Добавить пользователя в группу",
        tags=["Group"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id'],
            properties={'user_id': openapi.Schema(type=openapi.TYPE_INTEGER)}
        )
    )
    def add_user(self, request, pk=None):
        group = Group.objects.get(id=pk)
        user = User.objects.get(id=request.data.get('user_id'))

        if user in group.users.all():
            return Response({"detail": "⚠️ Пользователь уже в группе"}, status=400)

        if not group.can_add_user():
            return Response({"detail": "⚠️ Нет свободных мест"}, status=400)

        group.users.add(user)
        return Response({"detail": "Пользователь добавлен"})
    @action(detail=True, methods=['patch'], url_path='remove-user')
    @swagger_auto_schema(
        operation_summary="Удалить пользователя из группы",
        tags=["Group"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['telegram_id'],
            properties={'telegram_id': openapi.Schema(type=openapi.TYPE_INTEGER)}
        )
    )
    def remove_user(self, request, pk=None):
        group = Group.objects.get(id=pk)
        user = User.objects.get(telegram_id=request.data.get('telegram_id'))
        group.users.remove(user)
        return Response({"detail": "Пользователь удалён"})

"""
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from django.db.models import ProtectedError
#
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi 
#
from .models import Group
from .serializers import GroupSerializer
from account.permissions import IsAdmin
from account.auth import TelegramAuthentication
from account.models import User
from account.serializers import UserSerializer
"""


"""

class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [TelegramAuthentication]

    @swagger_auto_schema(
        operation_summary="Создать новую группу",
        operation_description="Только администратор может создать новую группу ",
        tags=["Group"],
        responses={201: GroupSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class GroupListView(APIView):
    authentication_classes = [TelegramAuthentication]

    @swagger_auto_schema(
        operation_summary="Список групп по дням",
        operation_description="Возвращает список групп, фильтруя по дням недели",
        tags=["Group"],
        manual_parameters=[
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Дни недели (например: 'mon/wed/fri')",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: GroupSerializer(many=True)}
    )

    def get(self, request):
        days = request.query_params.get('days')
        queryset = Group.objects.filter(days=days).order_by('time')
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)
    
class GroupDetailView(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [TelegramAuthentication]

    @swagger_auto_schema(
        operation_summary="Получить или обновить группу",
        operation_description="Только администратор может обновлять группу",
        tags=["Group"],
        responses={200: GroupSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить группу",
        operation_description="Только администратор может обновлять группу",
        tags=["Group"],
        responses={200: GroupSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class GetGroupUsersView(APIView):
    authentication_classes = [TelegramAuthentication]
    #
    permission_classes= [IsAdmin] #теперь только админ может видеть всех пользователей

    @swagger_auto_schema(
        operation_summary="Список пользователей группы",
        operation_description="Только администратор может видеть всех пользователей группы",
        tags=["Group"],
        responses={200: UserSerializer(many=True)}
    )
    #
    def get(self, requests, group_id):
        group = Group.objects.get(id=group_id)
        users = group.users.all()
        serialzier = UserSerializer(users, many=True)
        return Response(serialzier.data, status=200)

class GroupDeleteAPIView(APIView):
    authentication_classes = [TelegramAuthentication]

    @swagger_auto_schema(
        operation_summary="Удалить группу",
        operation_description="Только администратор может удалить группу",
        tags=["Group"],
        responses={200: "Группа удалена", 400: "Ошибка удаления"}
    )

    def delete(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
            group.delete()
            return Response({"datail":"Группа успешно удалена"})
        except ProtectedError:
            return Response({"detail":"❌ Невозможно удалить группу: в ней есть активные абонементы"}, status=400)
 ###       
class AddUserToGroupView(APIView):
    authentication_classes = [TelegramAuthentication]

    @swagger_auto_schema(
        operation_summary="Добавить пользователя в группу",
        operation_description="Добавляет пользователя в указанную группу, проверяет свободные места",
        tags=["Group"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['group_id','user_id'],
            properties={
                'group_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={200: "Пользователь добавлен", 400: "Ошибка добавления"}
    )

    def patch(self,request):
        group_id = request.data.get('group_id')
        user_id = request.data.get('user_id')

        group = Group.objects.get(id = group_id)
        user = User.objects.get(id = user_id)

        if user in group.users.all():
            return Response({"detail":"⚠️ Пользователь уже в группе"}, status= 400)
        
        if not group.can_add_user():
            return Response({"detail":"⚠️ Нет свободных мест"},status=400)
        
        group.users.add(user)

        return Response({
            "detail":"Пользователь добавлен",
            "group": group.as_text(),
            "free_slots": group.free_slots(),
            "users_now": group.get_users_count()
        }, status= 200)

class DeleteUserFromGroupView(APIView):
    authentication_classes= [TelegramAuthentication]

    @swagger_auto_schema(
        operation_summary="Удалить пользователя из группы",
        operation_description="Удаляет пользователя из группы по telegram_id",
        tags=["Group"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['group_id','telegram_id'],
            properties={
                'group_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'telegram_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={200: "Пользователь удалён"}
    )
    
    def patch(self, request):
        group_id = request.data.get('group_id')
        telegram_id = request.data.get('telegram_id')

        group = Group.objects.get(id = group_id)
        user = User.objects.get(telegram_id = telegram_id)

        group.user.remove(user)
        return Response({
            "detail":"Пользователь удалён",
            "free_slots": group.free_slots(),
        }, status=200)


@api_view(['PATCH'])
@authentication_classes([TelegramAuthentication])
def add_user_to_group(request):
    group_id = request.data.get('group_id')
    user_id = request.data.get('user_id')

    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)

    #
    if user in group.users.all():
        return Response({"detail:" "Пользователь уже состоит в этой группе"}, status=400)
    #

    group.users.add(user)
    return Response({'last_name':f"{user.last_name}", 'first_name':f"{user.first_name}", 'group_title':f"{group.title}",'group_time':f"{group.time}",'group_days':f"{group.days}"}, status=200)

@api_view(['PATCH'])
@authentication_classes([TelegramAuthentication])
def delete_user_from_group(request):
    group_id = request.data.get('group_id')
    telegram_id = request.data.get('telegram_id')

    group = Group.objects.get(id=group_id)
    user = User.objects.get(telegram_id=telegram_id)
    group.users.remove(user)
    return Response({'group_days':f'{group.days}'})


