from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, LikeViewSet, FavoriteViewSet

router = DefaultRouter()
router.register('comments',CommentViewSet,basename='comments')
router.register('likes',LikeViewSet, basename='likes')
router.register('favorites',FavoriteViewSet, basename='favorites')

urlpatterns = [
    path('', include(router.urls))
]
