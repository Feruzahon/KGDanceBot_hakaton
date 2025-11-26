from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
#
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
#
from .models import Comment, Like
from .serializers import CommentSerializer, LikeSerializer
from .permissions import IsOwnerOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group', 'user']
#для свагера описание
    @swagger_auto_schema(
        operation_summary="Создать новый комментарий",
        responses={201: CommentSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить список комментариев с фильтрацией",
        manual_parameters=[
            openapi.Parameter('group', openapi.IN_QUERY, description="ID группы", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user', openapi.IN_QUERY, description="ID пользователя", type=openapi.TYPE_INTEGER),
        ],
        responses={200: CommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
#
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
#
    @swagger_auto_schema(
        operation_summary="Поставить лайк",
        responses={201: LikeSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить список всех лайков",
        responses={200: LikeSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
#
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
