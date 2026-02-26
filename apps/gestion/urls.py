from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, TipoRegimenLaboralViewSet, ResponsableViewSet, LibroSocietarioViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'tipos-regimen-laboral', TipoRegimenLaboralViewSet)
router.register(r'responsables', ResponsableViewSet, basename='responsable')
router.register(r'libros-societarios', LibroSocietarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]