from rest_framework import serializers
from .models import Cliente, Credenciales

class CredencialesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credenciales
        exclude = ['cliente', 'id']

class ClienteSerializer(serializers.ModelSerializer):
    credenciales = CredencialesSerializer()

    class Meta:
        model = Cliente
        fields = '__all__'

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