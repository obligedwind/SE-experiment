from django.urls import path

from . import views


urlpatterns = [
    path('', views.sign_up, name='sign_up'),
    path('profile/',views.profile,name='profile'),
    path('user/',views.user,name='user'),
]
