from django.urls import path, include

from .views import GroupCreateView, GroupListView, GroupDetailView, GetGroupUsersView, GroupDeleteAPIView, add_user_to_group, delete_user_from_group
from .views import upload_group_image,delete_group_image
urlpatterns = [
    path('create/', GroupCreateView.as_view()),
    path('list/', GroupListView.as_view()),
    path('detail/<int:pk>/', GroupDetailView.as_view()),
    path('delete/<int:pk>/', GroupDeleteAPIView.as_view()),
    path('get_group_users/<int:group_id>/', GetGroupUsersView.as_view()),
    path('add_user/', add_user_to_group),
    path('delete_user/', delete_user_from_group),
    path('upload_image/<int:pk>/', upload_group_image),
    path('delete_image/<int:pk>/', delete_group_image),
]