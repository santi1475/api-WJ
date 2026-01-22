from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from .models import Cliente
from .serializers import ClienteSerializer
from .utils import generar_excel_masivo

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        user = self.request.user
        queryset = Cliente.objects.select_related('credenciales', 'responsable').all()
        
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