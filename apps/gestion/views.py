from rest_framework import viewsets, status, permissions, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from .models import Cliente, HistorialBaja, HistorialEstado, TipoRegimenLaboral, Responsable, LibroSocietario
from .serializers import ClienteSerializer, HistorialBajaSerializer, TipoRegimenLaboralSerializer, ResponsableSerializer, LibroSocietarioSerializer
from core_shared.utils.excel import generar_excel_masivo

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ['ruc', 'razon_social', 'propietario']
    
    def perform_create(self, serializer):
        cliente = serializer.save()
        HistorialEstado.objects.create(
            cliente=cliente,
            tipo_evento='INGRESO',
            fecha=cliente.fecha_ingreso or timezone.now().date(),
            usuario_responsable=self.request.user
        )
    
    def get_queryset(self):
        
        user = self.request.user
        queryset = Cliente.objects.select_related(
            'credenciales', 'responsable'
        ).prefetch_related(
            'historial_bajas__usuario_baja', 'libros_societarios'
        ).all()
        
        if self.action != 'retrieve' and not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(estado=True)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='dashboard-all')
    def dashboard_all(self, request):
        
        # Optimizacion vital: el dashboard no necesita credenciales ni libros, 
        # usar un queryset plano evita que count() sobrecargue la memoria de postgres con JOINS
        queryset = Cliente.objects.filter(estado=True)
        queryset = self.filter_queryset(queryset)
        
        # Import local para evitar ciclos si es necesario, o import global
        from .serializers import ClienteDashboardSerializer
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ClienteDashboardSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ClienteDashboardSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        
        queryset = Cliente.objects.filter(estado=True)
        
        total_activos = queryset.count()
        
        ingresos_totales = queryset.aggregate(
            total=Sum('ingresos_anuales')
        )['total'] or 0
        
        pendientes_declaracion = queryset.filter(
            ingresos_anuales=0
        ).count()
        
        return Response({
            'total_activos': total_activos,
            'ingresos_totales': str(ingresos_totales),
            'pendientes_declaracion': pendientes_declaracion
        })
        
    @action(detail=False, methods=['post'], url_path='exportar-seleccion')
    def exportar_seleccion(self, request):
        
        rucs = request.data.get('rucs', [])

        if not rucs:
            return Response(
                {"error": "No se seleccionaron clientes."}, 
                status=400
            )
            
        clientes_filtrados = Cliente.objects.filter(pk__in=rucs)
        wb = generar_excel_masivo(clientes_filtrados)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=Clientes_Seleccionados.xlsx'
        
        wb.save(response)
        return response
    
    @action(detail=False, methods=['get'], url_path='exportar-filtro')
    def exportar_filtro(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response(
                {"error": "No hay clientes que coincidan con la búsqueda."}, 
                status=400
            )
            
        wb = generar_excel_masivo(queryset)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=Clientes_Exportacion.xlsx'
        
        wb.save(response)
        return response
    
    @action(detail=False, methods=['post'], url_path='exportar-responsable')
    def exportar_responsable(self, request):
        responsables_ids = request.data.get('responsables_ids', [])
        
        if not responsables_ids:
            return Response(
                {"error": "No se seleccionaron responsables."}, 
                status=400
            )

        # Get all clients belonging to these responsables
        queryset = self.filter_queryset(self.get_queryset())
        
        # In case there's a "0" for "Sin responsable", handle it
        q_objects = Q()
        if 0 in responsables_ids or "0" in responsables_ids:
            q_objects |= Q(responsable__isnull=True)
            
        real_ids = [r for r in responsables_ids if r != 0 and r != "0"]
        if real_ids:
            q_objects |= Q(responsable_id__in=real_ids)
            
        clientes_filtrados = queryset.filter(q_objects)

        if not clientes_filtrados.exists():
            return Response(
                {"error": "No hay clientes asignados a los responsables seleccionados."}, 
                status=400
            )
            
        wb = generar_excel_masivo(clientes_filtrados)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=Clientes_Por_Responsable.xlsx'
        
        wb.save(response)
        return response

    @action(detail=False, methods=['get'], url_path='bajas')
    def listar_bajas(self, request):
        user = request.user
        queryset = Cliente.objects.filter(estado=False).select_related('credenciales', 'responsable')
        
        # if not (user.is_superuser or user.id == 1):
        #    queryset = queryset.filter(responsable=user)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='dar-baja')
    def dar_baja(self, request, pk=None):
        cliente = self.get_object()
        razon = request.data.get('razon', '')
        
        # Actualizamos estado actual
        cliente.estado = False
        cliente.fecha_baja = timezone.now().date()
        cliente.fecha_reactivacion = None
        cliente.save()

        # Registrar en historial
        HistorialBaja.objects.create(
            cliente=cliente,
            usuario_baja=request.user,
            razon=razon,
            estado='BAJA'
        )
        
        HistorialEstado.objects.create(
            cliente=cliente,
            tipo_evento='BAJA',
            fecha=cliente.fecha_baja,
            usuario_responsable=request.user
        )

        return Response({
            "code": 200,
            "message": f"Cliente {cliente.razon_social} dado de baja correctamente."
        })

    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        user = request.user
        try:
            cliente = Cliente.objects.get(pk=pk)
            if not (user.is_superuser or user.id == 1):
                if not cliente.responsable or cliente.responsable.nombre != user.username:
                    return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
        except Cliente.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        fecha_reactivacion = request.data.get('fecha', timezone.now().date())
        cliente.estado = True
        cliente.fecha_baja = None
        cliente.fecha_reactivacion = fecha_reactivacion
        cliente.save()

        # Actualizar último registro del historial (usamos .first() porque ordering es '-fecha_baja')
        ultimo_historial = HistorialBaja.objects.filter(cliente=cliente, estado='BAJA').first()
        if ultimo_historial:
            ultimo_historial.estado = 'REACTIVADO'
            ultimo_historial.fecha_reactivacion = timezone.now()
            ultimo_historial.save()
        HistorialEstado.objects.create(
            cliente=cliente,
            tipo_evento='REACTIVACION',
            fecha=fecha_reactivacion,
            usuario_responsable=request.user
        )
        
        return Response({
            "code": 200,
            "message": f"Cliente {cliente.razon_social} reactivado exitosamente."
        })

    @action(detail=False, methods=['get'], url_path='historial-bajas')
    def historial_bajas(self, request):
        """Obtiene el historial completo de todas las bajas de clientes"""
        user = request.user
        queryset = HistorialBaja.objects.select_related('cliente', 'usuario_baja').all()
        
        # Filtrar por responsable si no es superuser
        # Filtrar por responsable si no es superuser
        # if not (user.is_superuser or user.id == 1):
        #    queryset = queryset.filter(cliente__responsable=user)
        
        serializer = HistorialBajaSerializer(queryset, many=True)
        return Response(serializer.data)

class TipoRegimenLaboralViewSet(viewsets.ModelViewSet):
    queryset = TipoRegimenLaboral.objects.all()
    serializer_class = TipoRegimenLaboralSerializer
    permission_classes = [IsAuthenticated]
    
class ResponsableViewSet(viewsets.ModelViewSet):
    queryset = Responsable.objects.all()
    serializer_class = ResponsableSerializer
    permission_classes = [IsAuthenticated]

class LibroSocietarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LibroSocietario.objects.all()
    serializer_class = LibroSocietarioSerializer
    permission_classes = [IsAuthenticated]