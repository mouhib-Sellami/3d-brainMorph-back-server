from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import SimpleRouter
from brain_morph_server.viewsets.AuthViewSet import AuthViewSet
from brain_morph_server.viewsets.PermissionViewSet import PermissionViewSet
from brain_morph_server.viewsets.RoleViewSet import RoleViewSet
from brain_morph_server.viewsets.UserViewSet import UserViewSet
from brain_morph_server.viewsets.PatientViewSet import PatientViewSet
from brain_morph_server.viewsets.TaskViewSet import TaskViewSet

from . import views

router = SimpleRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)
