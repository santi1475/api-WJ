from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, TipoRegimenLaboralViewSet, ResponsableViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'tipos-regimen-laboral', TipoRegimenLaboralViewSet)
router.register(r'responsables', ResponsableViewSet, basename='responsable')

urlpatterns = [
    path('', include(router.urls)),
]