from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from django.db.models import ProtectedError

from .models import Group
from .serializers import GroupSerializer
from account.permissions import IsAdmin
from account.auth import TelegramAuthentication
from account.models import CustomUser
from account.serializers import UserSerializer

class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # permission_classes = [IsAdmin]


class GroupListView(APIView):
    def get(self, request):
        days = request.query_params.get('days')
        queryset = Group.objects.filter(days=days).order_by('time')
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)
    
class GroupDetailView(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class GetGroupUsersView(APIView):
    def get(self, requests, group_id):
        group = Group.objects.get(id=group_id)
        users = group.users.all()
        serialzier = UserSerializer(users, many=True)
        return Response(serialzier.data, status=200)

class GroupDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
            group.delete()
            return Response({"datail":"Группа успешно удалена"})
        except ProtectedError:
            return Response({"detail":"❌ Невозможно удалить группу: в ней есть активные абонементы"}, status=400)
        
        
@api_view(['PATCH'])
def add_user_to_group(request):
    group_id = request.data.get('group_id')
    group = Group.objects.get(id=group_id)
    if request.data.get('child_id'):
        child_id = request.data.get('child_id')
        # user = Child.objects.get(id=child_id)
    else:
        user_id = request.data.get('user_id')
        user = CustomUser.objects.get(id=user_id)
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