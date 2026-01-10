from django.urls import path
from . import views

urlpatterns = [
    # --- Clientes ---
    path('clientes/', views.cliente_list_create, name='cliente-list'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente-detail'),
    
    # --- Credenciales (Netflix, Bancos, etc - 1 a N) ---
    path('credenciales/', views.credencial_list, name='credencial-list'),
    path('credenciales/crear/', views.credencial_create, name='credencial-create'),
    path('credenciales/<int:pk>/', views.credencial_detail, name='credencial-detail'),
    
    # --- Datos Únicos (1 a 1) ---
    # Estas rutas sirven tanto para crear como para editar.
    # Solo necesitas enviar { "cliente": ID, ...datos... }
    path('datos-tributarios/gestionar/', views.datos_tributarios_manage, name='tributarios-manage'),
    path('cuenta-detraccion/gestionar/', views.cuenta_detraccion_manage, name='detraccion-manage'),
]
