"""
Haversine distance (km) from a reference point to each row's pickup coordinates.
Uses Django DB functions so it works with SQLite (3.35+ math) and PostgreSQL.
"""

from django.db.models import ExpressionWrapper, F, FloatField, Value
from django.db.models.functions import ASin, Cos, Power, Radians, Sin, Sqrt


def pickup_distance_km_expression(ref_lat: float, ref_lon: float):
    """
    Expression for great-circle distance in km from (ref_lat, ref_lon) to pickup point.
    """
    lat1 = Radians(Value(ref_lat, output_field=FloatField()))
    lon1 = Radians(Value(ref_lon, output_field=FloatField()))
    lat2 = Radians(F("pickup_latitude"))
    lon2 = Radians(F("pickup_longitude"))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    half_dlat = dlat * Value(0.5)
    half_dlon = dlon * Value(0.5)

    a = (
        Power(Sin(half_dlat), 2)
        + Cos(lat1) * Cos(lat2) * Power(Sin(half_dlon), 2)
    )
    central_angle = Value(2.0) * ASin(Sqrt(a))
    return ExpressionWrapper(
        Value(6371.0) * central_angle,
        output_field=FloatField(),
    )
