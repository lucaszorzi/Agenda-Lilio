from django.urls import path, include
from agenda import views


app_name = 'agenda'

urlpatterns = [

    path('', views.google_login),
    path('index', views.index, name='index'),

    # google callback
    path('googlecallback', views.google_authenticate, name='google_authenticate'),


    #path('accounts/', include('django.contrib.auth.urls'), name='login'),
    #path('accounts/', include('django.contrib.auth.urls'), name='logout'),

    path('event/all/', views.event_list_all, name='event_list_all'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/create/submit', views.event_create_submit, name='event_create_submit'),
    path('event/delete/<id>/', views.event_delete, name='event_delete'),

]
