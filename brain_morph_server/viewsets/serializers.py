from rest_framework import serializers
from brain_morph_server import models


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ('username', 'password',)


class changePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    class Meta:
        fields = ('old_password', 'new_password', 'confirm_password',)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active'
        )


class userProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
        )
