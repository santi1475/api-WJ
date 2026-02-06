from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from .serializers import (
    GroupSerializer, 
    PermissionSerializer, 
    CustomTokenObtainPairSerializer,
    UserSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]

    PROTECTED_ROLES = ['ADMIN', 'CONTADOR', 'ASISTENTE', 'CLIENTE']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "status": "success",
            "count": queryset.count(),
            "data": serializer.data
        })

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        if Group.objects.filter(name=name).exists():
            return Response({
                "code": 400,
                "message": f"El rol '{name}' ya existe."
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        new_name = request.data.get('name')
        if instance.name in self.PROTECTED_ROLES and new_name and new_name != instance.name:
            return Response({
                "code": 403,
                "message": f"No se puede renombrar el rol protegido del sistema: {instance.name}"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 200,
                "message": "Rol actualizado correctamente",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.name in self.PROTECTED_ROLES:
            return Response({
                "code": 403,
                "message": f"No se puede eliminar el rol protegido: {instance.name}"
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.user_set.exists():
            return Response({
                "code": 400,
                "message": "No se puede eliminar este rol porque hay usuarios asignados a él."
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "Rol eliminado correctamente"
        }, status=status.HTTP_200_OK)

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "status": "success",
            "count": queryset.count(),
            "data": serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "code": 201,
                "message": "Usuario creado exitosamente",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "code": 400,
            "message": "Error al crear usuario",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "status": "success",
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 200,
                "message": "Usuario actualizado correctamente",
                "data": serializer.data
            })
        return Response({
            "code": 400,
            "message": "Error al actualizar usuario",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": f"Usuario '{username}' eliminado correctamente"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def assign_roles(self, request, pk=None):
        """Endpoint específico para asignar roles a un usuario"""
        user = self.get_object()
        role_ids = request.data.get('roles', [])
        
        if not isinstance(role_ids, list):
            return Response({
                "code": 400,
                "message": "El campo 'roles' debe ser una lista de IDs"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            roles = Group.objects.filter(id__in=role_ids)
            user.groups.set(roles)
            
            serializer = self.get_serializer(user)
            return Response({
                "code": 200,
                "message": f"Roles asignados correctamente a {user.username}",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        user = self.get_object()
        permissions = user.get_all_permissions()
        
        return Response({
            "code": 200,
            "username": user.username,
            "permissions": list(permissions),
            "roles": [group.name for group in user.groups.all()]
        })