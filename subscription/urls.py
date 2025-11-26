from django.urls import path

from .views import CreateSubView, GetMySubView, GetChildSubView, GetUserSubView, mark_attendance, DeleteSubView

urlpatterns = [
    path('create_subscription/', CreateSubView.as_view()), 
    path('get_my_sub/', GetMySubView.as_view()),
    path('get_child_sub/', GetChildSubView.as_view()),
    path('get_user_sub/<int:user_id>/', GetUserSubView.as_view()),
    path('mark_attendance/<int:subscription_id>/', mark_attendance),
    path('delete_sub/<int:sub_id>/', DeleteSubView.as_view())
]