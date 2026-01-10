from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Cliente, DatosTributarios, CredencialPlataforma, CuentaDetraccion
from .serializers import (
    ClienteSerializer, 
    ClienteDetailSerializer,
    DatosTributariosSerializer,
    CredencialPlataformaSerializer,
    CuentaDetraccionSerializer
)

# -----------------------------------------------------------------------------
# UTILIDAD DE SEGURIDAD Y VALIDACIÓN LÓGICA
# -----------------------------------------------------------------------------
def validar_acceso_cliente(user, cliente_id):
    """
    Verifica permisos y estado lógico del cliente.
    1. Existe.
    2. No está eliminado lógicamente (estado != 'INACTIVO').
    3. Pertenece al usuario (o es Admin).
    """
    try:
        # Buscamos el cliente
        cliente = Cliente.objects.get(pk=cliente_id)
        
        # A. VALIDACIÓN DE ESTADO (Eliminación Lógica)
        # Si el cliente está inactivo, para el sistema "no existe" (excepto para admins si quisieran auditar)
        if cliente.estado == 'INACTIVO' and not user.is_superuser:
             return False, Response(
                {"detail": "Este cliente ha sido eliminado y no se pueden realizar acciones sobre él."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # B. VALIDACIÓN DE PERMISOS (Roles)
        if not user.is_superuser and cliente.responsable != user:
            return False, Response(
                {"detail": "No tienes permiso para gestionar este cliente."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        return True, cliente  # Retornamos el objeto cliente también para reutilizarlo
        
    except Cliente.DoesNotExist:
        return False, Response(
            {"detail": "Cliente no encontrado."}, 
            status=status.HTTP_404_NOT_FOUND
        )

# -----------------------------------------------------------------------------
# 1. CRUD CLIENTES
# -----------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cliente_list_create(request):
    """
    GET: Lista clientes activos.
    POST: Crea cliente nuevo.
    """
    # --- GET: LISTAR ---
    if request.method == 'GET':
        # Base Queryset
        clientes = Cliente.objects.all().order_by('razon_social')
        
        # 1. FILTRO DE ELIMINACIÓN LÓGICA
        # Por defecto, ocultamos los INACTIVOS
        if not request.query_params.get('ver_eliminados') == 'true':
            clientes = clientes.exclude(estado='INACTIVO')

        # 2. FILTRO DE ROLES
        if not request.user.is_superuser:
            clientes = clientes.filter(responsable=request.user)

        # 3. BUSCADOR
        search = request.query_params.get('search')
        if search:
            clientes = clientes.filter(
                Q(razon_social__icontains=search) | Q(ruc__icontains=search)
            )
            
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    # --- POST: CREAR ---
    elif request.method == 'POST':
        data = request.data.copy()
        
        # Asignar responsable si no es admin
        if not request.user.is_superuser:
            data['responsable'] = request.user.id
        
        # Forzar estado ACTIVO al crear
        data['estado'] = 'ACTIVO'
            
        serializer = ClienteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def cliente_detail(request, pk):
    """
    GET: Ver detalle.
    PUT: Editar.
    DELETE: Eliminación Lógica (cambia estado a INACTIVO).
    """
    # Reutilizamos la función de validación que ya maneja la lógica de "INACTIVO"
    ok, resultado = validar_acceso_cliente(request.user, pk)
    if not ok: return resultado # Si falla, retorna el error (404 o 403)
    
    cliente = resultado # El objeto cliente válido

    if request.method == 'GET':
        serializer = ClienteDetailSerializer(cliente)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ClienteSerializer(cliente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # --- ELIMINACIÓN LÓGICA ---
        cliente.estado = 'INACTIVO'
        cliente.save()
        
        return Response(
            {"message": "Cliente eliminado lógicamente. Sus datos se conservan pero no será visible."}, 
            status=status.HTTP_204_NO_CONTENT
        )


# -----------------------------------------------------------------------------
# 2. CRUD CREDENCIALES
# -----------------------------------------------------------------------------

# --- GET: LISTAR ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def credencial_list(request):
    """
    GET: Lista credenciales activas de los clientes del usuario.
    Parámetro opcional: cliente_id para filtrar por cliente específico
    """
    # Base queryset - solo credenciales activas
    credenciales = CredencialPlataforma.objects.filter(activo=True)
    
    # Si no es admin, solo ver credenciales de sus clientes
    if not request.user.is_superuser:
        credenciales = credenciales.filter(cliente__responsable=request.user)
    
    # Filtrar por cliente específico si se proporciona
    cliente_id = request.query_params.get('cliente_id')
    if cliente_id:
        ok, resultado = validar_acceso_cliente(request.user, cliente_id)
        if not ok: return resultado
        credenciales = credenciales.filter(cliente_id=cliente_id)
    
    serializer = CredencialPlataformaSerializer(credenciales, many=True)
    return Response({
        "code": 200,
        "status": "success",
        "count": credenciales.count(),
        "data": serializer.data
    })


# --- POST: CREAR ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def credencial_create(request):
    """Crear una nueva credencial"""
    cliente_id = request.data.get('cliente')
    
    # Validamos que el cliente exista, esté ACTIVO y el usuario tenga acceso
    ok, resultado = validar_acceso_cliente(request.user, cliente_id)
    if not ok: return resultado

    serializer = CredencialPlataformaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "code": 201,
            "message": "Credencial creada exitosamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        "code": 400,
        "message": "Error al crear credencial",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# --- GET/PUT/DELETE: DETALLE ---
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def credencial_detail(request, pk):
    """
    GET: Ver detalle de credencial.
    PUT: Editar credencial.
    DELETE: Soft delete de credencial (marca como inactiva).
    """
    credencial = get_object_or_404(CredencialPlataforma, pk=pk)

    # Validamos acceso al CLIENTE dueño de esta credencial
    ok, resultado = validar_acceso_cliente(request.user, credencial.cliente.id)
    if not ok: return resultado

    if request.method == 'GET':
        serializer = CredencialPlataformaSerializer(credencial)
        return Response({
            "code": 200,
            "status": "success",
            "data": serializer.data
        })

    elif request.method == 'PUT':
        serializer = CredencialPlataformaSerializer(credencial, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 200,
                "message": "Credencial actualizada correctamente",
                "data": serializer.data
            })
        return Response({
            "code": 400,
            "message": "Error al actualizar credencial",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # --- SOFT DELETE ---
        credencial.activo = False
        credencial.save()
        
        return Response({
            "code": 200,
            "message": "Credencial eliminada lógicamente"
        }, status=status.HTTP_200_OK)


# -----------------------------------------------------------------------------
# 3. GESTIÓN DATOS TRIBUTARIOS Y DETRACCIÓN (1 a 1)
# -----------------------------------------------------------------------------
# Estas funciones no necesitan eliminación lógica explícita porque
# si el Cliente está INACTIVO, la función 'validar_acceso_cliente' 
# bloqueará el acceso a estos endpoints automáticamente.

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def datos_tributarios_manage(request):
    cliente_id = request.data.get('cliente')
    
    ok, resultado = validar_acceso_cliente(request.user, cliente_id)
    if not ok: return resultado

    try:
        instancia = DatosTributarios.objects.get(cliente_id=cliente_id)
        serializer = DatosTributariosSerializer(instancia, data=request.data, partial=True)
    except DatosTributarios.DoesNotExist:
        serializer = DatosTributariosSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def cuenta_detraccion_manage(request):
    cliente_id = request.data.get('cliente')
    
    ok, resultado = validar_acceso_cliente(request.user, cliente_id)
    if not ok: return resultado

    try:
        instancia = CuentaDetraccion.objects.get(cliente_id=cliente_id)
        serializer = CuentaDetraccionSerializer(instancia, data=request.data, partial=True)
    except CuentaDetraccion.DoesNotExist:
        serializer = CuentaDetraccionSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- DASHBOARD Y DEMO ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Datos del dashboard para el usuario autenticado"""
    total_clientes = Cliente.objects.filter(responsable=request.user).exclude(estado='INACTIVO').count() if not request.user.is_superuser else Cliente.objects.exclude(estado='INACTIVO').count()
    
    return Response({
        "total_clientes": total_clientes,
        "usuario": request.user.username
    })


@api_view(['GET'])
def holamundo(request):
    """Endpoint de prueba"""
    return Response({"message": "¡Hola Mundo!"})