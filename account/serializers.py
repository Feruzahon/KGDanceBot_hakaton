from rest_framework import serializers

from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user 
    
# class ChildSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Child
#         fields = '__all__'

    # def create(self, validated_data):
    #     validated_data['parent'] = self.context['request'].user
    #     return super().create(validated_data)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)

        # Это попадёт в JSON-ответ сервера
        data['id'] = self.user.id
        data['role'] = self.user.role
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data
    
    




