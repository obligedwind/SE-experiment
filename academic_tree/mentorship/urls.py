from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('append/',views.append,name='append'),
    path('view/',views.view,name='view'),
    path('delete/',views.delete,name='delete'),
    path('adjust/',views.adjust,name='adjust'),
    path('name_a/',views.name_a,name='name_a'),
    path('url_a/',views.url_a,name='url_a'),
    path('time_a/',views.time_a,name='time_a'),
    path('review/',views.review,name ='review'),
    path('total/',views.total,name='total'),
    path('total_view/',views.total_view,name='total_view'),
    # path('graph/', views.graph_view, name='graph'),
]
