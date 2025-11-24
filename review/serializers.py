from rest_framework import serializers
from .models import Comment,Like


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    like_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model=Comment
        fields = '__all__'
#количество лайков
    def get_like_count(self, obj):
        return obj.likes.count()
    #
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only = True)

    class Meta:
        model = Like
        fields = '__all__'