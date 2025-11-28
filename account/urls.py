from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import TelegramRegisterView, ActivateView ,ChildRegisterView, CheckRoleView, GetChildsView, GetUserView, MyTokenObtainPairView, PasswordResetAPIView,PasswordResetConfirmAPIView

urlpatterns = [
    path('register/', TelegramRegisterView.as_view()),
    path('activate/', ActivateView.as_view()),
    path('password_reset/', PasswordResetAPIView.as_view()),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view()),
    path('login/', MyTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('child_register/', ChildRegisterView.as_view()),
    path('check_role/', CheckRoleView.as_view()),
    path('get_user/', GetUserView.as_view()),
    path('get_childs/', GetChildsView.as_view())
]