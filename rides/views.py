from datetime import timedelta

from django.db.models import Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rides.expressions import pickup_distance_km_expression
from rides.filters import RideFilter
from rides.models import Ride, RideEvent, User
from rides.permissions import IsAdminRole
from rides.serializers import (
    RideEventSerializer,
    RideSerializer,
    RideWriteSerializer,
    UserSerializer,
)


def _ride_queryset_with_prefetch():
    cutoff = timezone.now() - timedelta(hours=24)
    return (
        Ride.objects.select_related("rider", "driver")
        .prefetch_related(
            Prefetch(
                "ride_events",
                queryset=RideEvent.objects.filter(occurred_at__gte=cutoff).order_by(
                    "occurred_at"
                ),
                to_attr="_todays_ride_events",
            )
        )
        .all()
    )


class RideViewSet(viewsets.ModelViewSet):
    """
    List/create/update/delete rides.
    List supports filters, ordering by pickup_time or distance (requires ref_lat/ref_lon), pagination.
    """

    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RideFilter

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RideWriteSerializer
        return RideSerializer

    def get_queryset(self):
        return _ride_queryset_with_prefetch()

    def _serialize_ride_read(self, ride):
        qs = _ride_queryset_with_prefetch().filter(pk=ride.pk)
        obj = qs.first()
        return RideSerializer(obj, context=self.get_serializer_context()).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        return Response(
            self._serialize_ride_read(ride),
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        return Response(self._serialize_ride_read(ride))

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return self._apply_ordering(queryset)

    def _apply_ordering(self, queryset):
        ordering = self.request.query_params.get("ordering", "-pickup_time").strip()
        if ordering in ("distance", "-distance"):
            try:
                ref_lat = float(self.request.query_params["ref_lat"])
                ref_lon = float(self.request.query_params["ref_lon"])
            except (KeyError, ValueError, TypeError) as exc:
                raise ValidationError(
                    {
                        "detail": "ordering=distance requires numeric ref_lat and ref_lon query parameters."
                    }
                ) from exc
            queryset = queryset.annotate(
                distance_km=pickup_distance_km_expression(ref_lat, ref_lon)
            )
            if ordering == "distance":
                return queryset.order_by("distance_km", "id")
            return queryset.order_by("-distance_km", "id")
        if ordering in ("pickup_time", "-pickup_time"):
            return queryset.order_by(ordering, "id")
        return queryset.order_by("-pickup_time", "id")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]


class RideEventViewSet(viewsets.ModelViewSet):
    queryset = RideEvent.objects.select_related("ride")
    serializer_class = RideEventSerializer
    permission_classes = [IsAdminRole]
