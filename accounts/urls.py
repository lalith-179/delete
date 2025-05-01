from django.urls import path
from . import views

urlpatterns = [
    path('usersignin/', views.user_login, name='user_login'),
    path('usersignup/', views.user_signup, name='user_signup'),
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('logout/', views.signout, name="logout"), 
     path('usersignin/', views.user_login, name='user login'),
    path('userregister/', views.user_signup, name='user register'),
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('logout/', views.signout, name="logout"), 
]