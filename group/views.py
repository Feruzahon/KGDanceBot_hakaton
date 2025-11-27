from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import ProtectedError
#
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi 
#
from .models import Group
from .serializers import GroupSerializer
from account.permissions import IsAdmin
from account.models import CustomUser
from account.serializers import UserSerializer
from .paginations import GroupPagination

class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Создать новую группу",
        operation_description="Только администратор может создать новую группу ",
        tags=["Group"],
        responses={201: GroupSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class GroupListView(APIView):
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

        paginator = GroupPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = GroupSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class GroupDetailView(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

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

    permission_classes= [IsAdmin] #теперь только админ может видеть всех пользователей

    @swagger_auto_schema(
        operation_summary="Список пользователей группы",
        operation_description="Только администратор может видеть всех пользователей группы",
        tags=["Group"],
        responses={200: UserSerializer(many=True)}
    )

    def get(self, requests, group_id):
        group = Group.objects.get(id=group_id)
        users = group.users.all()
        serialzier = UserSerializer(users, many=True)
        return Response(serialzier.data, status=200)

class GroupDeleteAPIView(APIView):
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
      
# class AddUserToGroupView(APIView):
#     authentication_classes = [TelegramAuthentication]

#     @swagger_auto_schema(
#         operation_summary="Добавить пользователя в группу",
#         operation_description="Добавляет пользователя в указанную группу, проверяет свободные места",
#         tags=["Group"],
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=['group_id','user_id'],
#             properties={
#                 'group_id': openapi.Schema(type=openapi.TYPE_INTEGER),
#                 'user_id': openapi.Schema(type=openapi.TYPE_INTEGER)
#             }
#         ),
#         responses={200: "Пользователь добавлен", 400: "Ошибка добавления"}
#     )

#     def patch(self,request):
#         group_id = request.data.get('group_id')
#         user_id = request.data.get('user_id')

#         group = Group.objects.get(id = group_id)
#         user = CustomUser.objects.get(id = user_id)

#         if user in group.users.all():
#             return Response({"detail":"⚠️ Пользователь уже в группе"}, status= 400)
        
#         if not group.can_add_user():
#             return Response({"detail":"⚠️ Нет свободных мест"},status=400)
        


# class DeleteUserFromGroupView(APIView):

#     @swagger_auto_schema(
#         operation_summary="Удалить пользователя из группы",
#         operation_description="Удаляет пользователя из группы по telegram_id",
#         tags=["Group"],
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=['group_id','telegram_id'],
#             properties={
#                 'group_id': openapi.Schema(type=openapi.TYPE_INTEGER),
#                 'telegram_id': openapi.Schema(type=openapi.TYPE_INTEGER)
#             }
#         ),
#         responses={200: "Пользователь удалён"}
#     )
    
#     def patch(self, request):
#         group_id = request.data.get('group_id')
#         telegram_id = request.data.get('telegram_id')

#         group = Group.objects.get(id = group_id)
#         user = CustomUser.objects.get(telegram_id = telegram_id)

#         group.user.remove(user)
#         return Response({
#             "detail":"Пользователь удалён",
#             "free_slots": group.free_slots(),
#         }, status=200)


@api_view(['PATCH'])
def add_user_to_group(request):
    group_id = request.data.get('group_id')
    group = Group.objects.get(id=group_id)
    user_id = request.data.get('user_id')
    user = CustomUser.objects.get(id=user_id)
    if user in group.users.all():
        return Response({"detail:" "Пользователь уже состоит в этой группе"}, status=400)
    
    group.users.add(user)
    return Response({'last_name':f"{user.last_name}", 'first_name':f"{user.first_name}", 'group_title':f"{group.title}",'group_time':f"{group.time}",'group_days':f"{group.days}"}, status=200)

@api_view(['PATCH'])
def delete_user_from_group(request):
    group_id = request.data.get('group_id')
    id = request.data.get('user_id')

    group = Group.objects.get(id=group_id)
    user = CustomUser.objects.get(id=id)
    group.users.remove(user)
    return Response({'group_days':f'{group.days}'})

