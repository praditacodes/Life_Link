from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import custom_logout

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_update_view, name='profile'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('dashboard/', views.user_dashboard_view, name='user-dashboard'),
]

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
LogoutView.dispatch = method_decorator(csrf_exempt, name='dispatch')(LogoutView.dispatch)
LogoutView.http_method_names = ['get', 'post', 'head', 'options', 'trace'] 