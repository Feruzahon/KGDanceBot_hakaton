from rest_framework import serializers
from .models import Group #
from account.serializers import UserSerializer# 

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['id', 'users']
    
    user_count = serializers.SerializerMethodField()
    teacher = UserSerializer(read_only = True) # добавленипе тренена (препода)
    def get_user_count(self, obj):
        return obj.get_users_count()