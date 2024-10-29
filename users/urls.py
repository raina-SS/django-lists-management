from django.urls import path
from . import views

# from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout_user, name='logout'),
]
