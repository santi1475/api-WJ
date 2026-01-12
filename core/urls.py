from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de Autenticación
    path('api/auth/', include('authentication.urls')),
    
    # Rutas de Gestión (ERP)
    path('api/gestion/', include('gestion.urls')),
]