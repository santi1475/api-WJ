from rest_framework import serializers
from .models import Cliente, Credenciales, HistorialBaja, TipoRegimenLaboral

class CredencialesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credenciales
        exclude = ['cliente', 'id']

class ResponsableSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    
class TipoRegimenLaboralSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRegimenLaboral
        fields = '__all__'

class HistorialBajaSerializer(serializers.ModelSerializer):
    usuario_baja_info = serializers.SerializerMethodField()
    cliente_info = serializers.SerializerMethodField()

    class Meta:
        model = HistorialBaja
        fields = ['id', 'cliente', 'cliente_info', 'fecha_baja', 'fecha_reactivacion', 'usuario_baja', 'usuario_baja_info', 'razon', 'estado']
        read_only_fields = ['id', 'fecha_baja']

    def get_usuario_baja_info(self, obj):
        if obj.usuario_baja:
            return {
                'id': obj.usuario_baja.id,
                'username': obj.usuario_baja.username,
                'first_name': obj.usuario_baja.first_name or '',
                'last_name': obj.usuario_baja.last_name or '',
                'full_name': self._get_full_name(obj.usuario_baja)
            }
        return None

    def get_cliente_info(self, obj):
        return {
            'ruc': obj.cliente.ruc,
            'razon_social': obj.cliente.razon_social,
            'estado': obj.cliente.estado,
            'tipo_empresa': obj.cliente.tipo_empresa,
            'categoria': obj.cliente.categoria
        }

    def _get_full_name(self, user):
        """Retorna el nombre completo o username si no hay nombre"""
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}".strip()
        elif user.first_name:
            return user.first_name
        elif user.last_name:
            return user.last_name
        else:
            return user.username

class ClienteSerializer(serializers.ModelSerializer):
    credenciales = CredencialesSerializer()
    responsable_info = serializers.SerializerMethodField()
    historial = HistorialBajaSerializer(source='historial_bajas', many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_responsable_info(self, obj):
        if obj.responsable:
            return {
                'id': obj.responsable.id,
                'username': obj.responsable.username,
                'first_name': obj.responsable.first_name or '',
                'last_name': obj.responsable.last_name or '',
                'email': obj.responsable.email or '',
                'full_name': self._get_full_name(obj.responsable)
            }
        return None

    def _get_full_name(self, user):
        """Retorna el nombre completo o username si no hay nombre"""
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}".strip()
        elif user.first_name:
            return user.first_name
        elif user.last_name:
            return user.last_name
        else:
            return user.username

    def create(self, validated_data):
        credenciales_data = validated_data.pop('credenciales')
        cliente = Cliente.objects.create(**validated_data)
        Credenciales.objects.create(cliente=cliente, **credenciales_data)
        return cliente

    def update(self, instance, validated_data):
        credenciales_data = validated_data.pop('credenciales', None)
        # Actualizar Cliente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Actualizar Credenciales
        if credenciales_data:
            for attr, value in credenciales_data.items():
                setattr(instance.credenciales, attr, value)
            instance.credenciales.save()
        return instance