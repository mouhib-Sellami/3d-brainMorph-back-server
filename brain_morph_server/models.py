from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from engine import models as engineModels
from django.conf import settings

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def attributes(self):
        return self.__dict__

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(
        self,
        username,
        password,
        email,
        first_name='',
        last_name='',
        is_superuser=False,
        is_admin=False,
        is_staff=False,
        **extra_fields,
    ):
        if not username:
            raise ValueError('Username can not be null.')
        user = self.model(
            username=username,
            is_superuser=is_superuser,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            is_staff=is_staff,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username, email=email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.email = email
        user.is_staff = True
        user.first_name = ''
        user.last_name = ''
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, BaseModel):
    username = models.CharField(
        max_length=255, unique=True, blank=False, null=False)
    email = models.EmailField(
        max_length=255, unique=True, blank=False, null=False, default=''
    )
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    role = models.ForeignKey('Role', on_delete=models.CASCADE, null=True)
    objects = UserManager()

    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True


class AppPermission(BaseModel):
    label = models.CharField(max_length=255, null=False,
                             blank=True, default="", unique=True)

    def __str__(self) -> str:
        return self.label


class Role(BaseModel):
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    slug = models.CharField(max_length=255, default='', null=True, blank=True)
    permissions = models.ManyToManyField(
        AppPermission, related_name='role_permission')
    active = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Patient(BaseModel):
    class Gender(models.TextChoices):
        male = "Male"
        female = "Female"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    folder_name = models.UUIDField(default=uuid.uuid4, editable=False)
    birth_date = models.DateField(null=True)
    age = models.IntegerField(null=True, default=0)
    gender = models.CharField(
        max_length=255, default="", null=True, choices=Gender.choices)
    is_generated = models.BooleanField(default=False)
    has_files = models.BooleanField(default=False)
    brain_file_path = models.TextField(null=True, default="")
    brain_combine_file_path = models.TextField(null=True, default="")
    tumor_file_path = models.TextField(null=True, default="")
    nii_file_path = models.TextField(null=True, default="")
    rapport_file_path = models.TextField(null=True, default="")
    is_processing = models.BooleanField(default=False)


class JobClientArtifact(engineModels.JobBaseModal):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    download_folder_path = models.TextField(blank=True, default="")
