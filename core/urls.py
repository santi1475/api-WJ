from django.contrib import admin
from django.urls import path, include
from gestion import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')), 
    
    # Rutas de gestión
    path('api/dashboard/', views.dashboard_data),
    path('hola/', views.holamundo),
]