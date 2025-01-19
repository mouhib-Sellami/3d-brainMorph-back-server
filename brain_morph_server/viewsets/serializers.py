from rest_framework import serializers
from brain_morph_server import models


class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppPermission
        fields = '__all__'


class RoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = '__all__'


class RoleReadSerializer(serializers.ModelSerializer):
    permissions = AppPermissionSerializer(many=True)

    class Meta:
        model = models.Role
        fields = '__all__'


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ('username', 'password',)


class UserSerializer(serializers.ModelSerializer):
    role = RoleReadSerializer(read_only=True)

    class Meta:
        model = models.User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'role',
            'created_at'
        )


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'role'
        )
