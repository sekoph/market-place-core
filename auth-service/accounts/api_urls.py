from django.urls import path
from . import views

urlpatterns = [
    path('public/', views.PublicView.as_view(), name='public'),
    path('authenticated/', views.AuthenticatedView.as_view(), name='authenticated'),
    path('admin/', views.AdminOnlyView.as_view(), name='admin_only'),
    path('user/', views.UserView.as_view(), name='user_only'),
]