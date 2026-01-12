from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    # select_related optimiza la consulta SQL para traer credenciales de golpe
    queryset = Cliente.objects.select_related('credenciales').all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]