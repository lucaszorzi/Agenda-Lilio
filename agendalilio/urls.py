from django.contrib import admin
from django.urls import path
from django.urls.conf import include


urlpatterns = [

    path('', include('agenda.urls', namespace='agenda')),

    path('accounts/', include('allauth.urls')),

    path('admin/', admin.site.urls),
]