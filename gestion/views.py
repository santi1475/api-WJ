from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra los clientes según el rol del usuario y la acción:
        - Admin (id=1) y Superadmin: ven todos los clientes
        - Otros usuarios en 'dashboard_all': ven todos los clientes (solo lectura)
        - Otros usuarios: solo ven los clientes asignados a ellos
        """
        user = self.request.user
        queryset = Cliente.objects.select_related('credenciales', 'responsable').all()
        
        # Si es superadmin o admin (id=1), devolver todos los clientes
        if user.is_superuser or user.id == 1:
            return queryset
        
        # Para otros usuarios, filtrar solo clientes asignados a ese responsable
        return queryset.filter(responsable=user)
    
    @action(detail=False, methods=['get'], url_path='dashboard-all')
    def dashboard_all(self, request):
        """
        Retorna TODOS los clientes de la empresa (sin filtrar por responsable)
        para mostrarse en el dashboard principal (solo lectura)
        """
        queryset = Cliente.objects.select_related('credenciales', 'responsable').all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Retorna estadísticas de TODOS los clientes de la empresa
        (sin filtrar por responsable) para el dashboard
        """
        # Usar todos los clientes de la empresa para las estadísticas
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