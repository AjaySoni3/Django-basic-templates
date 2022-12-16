from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_api_view, name='register'),
    path('login/', views.login_api_view, name='login'),
    path('profile/', views.user_profile, name='user_profile'),
    path('changepassword/', views.user_change_password, name='change_password'),
    path('sendresetpassword/', views.send_reset_password, name='send_reset_password'),
    path('resetpassword/<uid>/<token>/', views.user_reset_password, name='reset_password'),
]
