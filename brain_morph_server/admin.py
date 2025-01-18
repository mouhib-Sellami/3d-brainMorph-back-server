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

admin.site.register(models.User, UserAdmin)

