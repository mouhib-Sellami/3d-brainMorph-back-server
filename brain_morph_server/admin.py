from django.contrib import admin
from . import models
# Register your models here.
list_page = 20


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "is_superuser",
        "is_admin",
        "is_staff",
        "is_active",
        "created_at",
        "updated_at",
    ]
    ordering = ["created_at"]
    list_per_page = list_page


class AppPermissionsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "created_at",
        "updated_at",
    ]
    ordering = ["created_at"]
    list_per_page = list_page


class RoleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "slug",
        "active",
        "created_at",
        "updated_at",
    ]
    ordering = ["created_at"]
    list_per_page = list_page


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.Patient)
admin.site.register(models.JobClientArtifact)
admin.site.register(models.AppPermission, AppPermissionsAdmin)
