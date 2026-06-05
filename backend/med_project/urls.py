from django.contrib import admin
from django.urls import path, include
from med_project.api.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('med_project.api.urls')),
    path('', home_view, name='home'),
]

