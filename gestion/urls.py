from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

# El Router crea automáticamente las rutas del CRUD (GET, POST, PUT, DELETE)
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')

urlpatterns = [
    # Esto incluye todas las rutas generadas por el router
    path('', include(router.urls)),
]