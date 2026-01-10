from rest_framework import serializers
from .models import Cliente, DatosTributarios, CredencialPlataforma, CuentaDetraccion

class DatosTributariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosTributarios
        fields = '__all__'

class CuentaDetraccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaDetraccion
        fields = '__all__'

class CredencialPlataformaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredencialPlataforma
        fields = '__all__'

# Serializer simple para listados (carga rápida)
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

# Serializer detallado para ver UN cliente con TODO (carga completa)
class ClienteDetailSerializer(serializers.ModelSerializer):
    datos_tributarios = DatosTributariosSerializer(read_only=True)
    cuenta_detraccion = CuentaDetraccionSerializer(read_only=True)
    credenciales = CredencialPlataformaSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'