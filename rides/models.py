from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_USER = "user"

    role = models.CharField(max_length=32, default=ROLE_USER, db_index=True)
    phone_number = models.CharField(max_length=32, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return self.email or self.username


class Ride(models.Model):
    STATUS_EN_ROUTE = "en-route"
    STATUS_PICKUP = "pickup"
    STATUS_DROPOFF = "dropoff"

    STATUS_CHOICES = [
        (STATUS_EN_ROUTE, "en-route"),
        (STATUS_PICKUP, "pickup"),
        (STATUS_DROPOFF, "dropoff"),
    ]

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, db_index=True)
    rider = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rides_as_rider",
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rides_as_driver",
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["pickup_time"]),
            models.Index(fields=["status", "pickup_time"]),
        ]

    def __str__(self) -> str:
        return f"Ride {self.pk} ({self.status})"


class RideEvent(models.Model):
    """Event tied to a ride; `occurred_at` is used for the 24h window and reporting."""

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="ride_events",
    )
    description = models.TextField()
    occurred_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["ride", "occurred_at"]),
        ]
        ordering = ["occurred_at"]

    def __str__(self) -> str:
        return f"RideEvent {self.pk} on ride {self.ride_id}"
