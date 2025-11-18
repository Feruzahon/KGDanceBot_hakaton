from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    

    # def create(self, validated_data):
    #     if validated_data['role'] != 'student':
    #         validated_data['parent'] = None
    #     validated_data['parent'] = self.context['request'].user
    #     return super().create(validated_data)



