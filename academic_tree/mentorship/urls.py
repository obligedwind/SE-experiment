from django.urls import path

from . import views


urlpatterns = [
    path('', views.node_detail, name='node_detail'),
]
