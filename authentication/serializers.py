from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.contenttypes.models import ContentType
import rest_framework.serializers as serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.models import Group, Permission

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')

        if username_or_email and password:
            if '@' in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    attrs['username'] = user.username
                except User.DoesNotExist:
                    pass
        
        data = super().validate(attrs)
        if self.user:
            permissions = list(self.user.get_all_permissions())
            
            data.update({
                'code': 200,  
                'user': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'email': self.user.email,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'is_superuser': self.user.is_superuser,
                    'is_staff': self.user.is_staff,
                },
                'permissions': permissions
            })

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']