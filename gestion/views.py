from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from .models import Cliente, HistorialBaja, HistorialEstado, TipoRegimenLaboral
from .serializers import ClienteSerializer, HistorialBajaSerializer, TipoRegimenLaboralSerializer
from .utils import generar_excel_masivo

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    
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
        queryset = Cliente.objects.select_related('credenciales', 'responsable').all()
        
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(estado=True)
        
        if user.is_superuser or user.id == 1:
            return queryset
        
        return queryset.filter(responsable=user)
    
    @action(detail=False, methods=['get'], url_path='dashboard-all')
    def dashboard_all(self, request):
        
        queryset = Cliente.objects.select_related('credenciales', 'responsable').all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        
        queryset = Cliente.objects.all()
        
        # Total de clientes activos
        total_activos = queryset.filter(estado=True).count()
        
        # Ingresos totales (suma de ingresos anuales)
        ingresos_totales = queryset.aggregate(
            total=Sum('ingresos_anuales')
        )['total'] or 0
        
        # Pendientes de declaración (clientes activos sin ingresos reportados)
        pendientes_declaracion = queryset.filter(
            estado=True,
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
        wb = generar_excel_masivo(rucs)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=Clientes_Seleccionados.xlsx'
        
        wb.save(response)
        return response
    
    @action(detail=False, methods=['get'], url_path='bajas')
    def listar_bajas(self, request):
        user = request.user
        queryset = Cliente.objects.filter(estado=False).select_related('credenciales', 'responsable')
        
        if not (user.is_superuser or user.id == 1):
            queryset = queryset.filter(responsable=user)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='dar-baja')
    def dar_baja(self, request, pk=None):
        cliente = self.get_object()
        razon = request.data.get('razon', '')
        
        # Actualizamos estado actual
        cliente.estado = False
        cliente.estado = False
        cliente.fecha_baja = timezone.now().date()
        cliente.save()

        # Registrar en historial
        HistorialBaja.objects.create(
            cliente=cliente,
            usuario_baja=request.user,
            razon=razon,
            estado='BAJA'
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
            if not (user.is_superuser or user.id == 1) and cliente.responsable != user:
                return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
        except Cliente.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        fecha_reactivacion = request.data.get('fecha', timezone.now().date())
        cliente.estado = True
        cliente.fecha_baja = None 
        cliente.save()

        # Actualizar último registro del historial
        ultimo_historial = HistorialBaja.objects.filter(cliente=cliente, estado='BAJA').last()
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
        if not (user.is_superuser or user.id == 1):
            queryset = queryset.filter(cliente__responsable=user)
        
        serializer = HistorialBajaSerializer(queryset, many=True)
        return Response(serializer.data)

class TipoRegimenLaboralViewSet(viewsets.ModelViewSet):
    queryset = TipoRegimenLaboral.objects.all()
    serializer_class = TipoRegimenLaboralSerializer
    permission_classes = [IsAuthenticated]