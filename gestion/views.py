from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from .models import Cliente
from .serializers import ClienteSerializer
from .utils import generar_excel_masivo

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        user = self.request.user
        queryset = Cliente.objects.select_related('credenciales', 'responsable').all()
        
        # --- LÓGICA DE FILTRADO (SOFT DELETE) ---
        # Por defecto, solo mostramos los activos.
        # Si quieres ver todo (para depurar), podrías pasar ?include_deleted=true en la URL
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(estado=True)
        # ----------------------------------------
        
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
        
        cliente.estado = False
        cliente.fecha_baja = timezone.now().date()
        cliente.save()

        return Response({
            "code": 200,
            "message": f"Cliente {cliente.razon_social} dado de baja correctamente."
        })

    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        """Restaura un cliente dado de baja"""
        user = request.user
        
        try:
            cliente = Cliente.objects.get(pk=pk)
            
            # Verificación de seguridad manual (ya que nos saltamos get_queryset)
            if not (user.is_superuser or user.id == 1) and cliente.responsable != user:
                return Response(
                    {"error": "No tienes permiso para reactivar este cliente"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
        except Cliente.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cliente.estado = True
        cliente.fecha_baja = None
        cliente.save()
        
        return Response({
            "code": 200,
            "message": f"Cliente {cliente.razon_social} reactivado exitosamente."
        })