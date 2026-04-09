from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from rides.models import Ride, RideEvent, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Wingz", {"fields": ("role", "phone_number")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (None, {"fields": ("role", "phone_number")}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "rider", "driver", "pickup_time")
    list_filter = ("status",)
    raw_id_fields = ("rider", "driver")


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ("id", "ride", "occurred_at")
    list_filter = ("occurred_at",)
    raw_id_fields = ("ride",)
