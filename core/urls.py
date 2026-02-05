from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')), # Actualizado
    path('api/gestion/', include('apps.gestion.urls')),     # Actualizado
]