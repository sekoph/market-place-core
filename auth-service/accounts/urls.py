from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth-url/', views.AuthUrlView.as_view(), name='auth_url'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.RefreshTokenView.as_view(), name='refresh_token'),
    path('user-info/', views.UserInfoView.as_view(), name='user_info'),
    path('register/', views.RegisterView.as_view(), name='user_registration'),
    path('loginn/', views.KeyCloakLoginView.as_view(), name='keycloak-login'),
]