import os
from dotenv import load_dotenv
from rest_framework import serializers
from brain_morph_server import models
from engine import models as engineModels

load_dotenv()


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


class PatientSerializer(serializers.ModelSerializer):
    public_tumor = serializers.SerializerMethodField('get_tumor_public_link')
    public_brain = serializers.SerializerMethodField('get_brain_public_link')
    public_rapport = serializers.SerializerMethodField('get_rapport_public_link')
    public_combined_brain = serializers.SerializerMethodField(
        'get_combined_brain_public_link')

    class Meta:
        fields = '__all__'
        model = models.Patient

    def get_tumor_public_link(self, obj: models.Patient):
        return os.getenv('MINIO_HOST_PROTOCOL') + os.getenv('MINIO_HOST') + "/" + obj.tumor_file_path

    def get_brain_public_link(self, obj: models.Patient):
        return os.getenv('MINIO_HOST_PROTOCOL') + os.getenv('MINIO_HOST') + "/" + obj.brain_file_path

    def get_combined_brain_public_link(self, obj: models.Patient):
        return os.getenv('MINIO_HOST_PROTOCOL') + os.getenv('MINIO_HOST') + "/" + obj.brain_combine_file_path
    
    def get_rapport_public_link(self, obj: models.Patient):
        return os.getenv('MINIO_HOST_PROTOCOL') + os.getenv('MINIO_HOST') + "/" + obj.rapport_file_path


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('first_name', 'last_name', 'birth_date', 'age', 'gender')
        model = models.Patient


class JobSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()

    class Meta:
        model = models.JobClientArtifact
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    job_payload = JobSerializer()

    class Meta:
        model = engineModels.Task
        fields = '__all__'
