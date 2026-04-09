from rest_framework import serializers

from rides.models import Ride, RideEvent, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "role",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
        )

    def create(self, validated_data):
        password = validated_data.pop("password", None) or None
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = ("id", "ride", "description", "occurred_at")


class RideSerializer(serializers.ModelSerializer):
    id_rider = serializers.IntegerField(source="rider_id", read_only=True)
    id_driver = serializers.IntegerField(source="driver_id", read_only=True)
    rider = UserSerializer(read_only=True)
    driver = UserSerializer(read_only=True)
    todays_ride_events = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = (
            "id",
            "status",
            "id_rider",
            "id_driver",
            "rider",
            "driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
            "todays_ride_events",
        )

    def get_todays_ride_events(self, obj):
        events = getattr(obj, "_todays_ride_events", None)
        if events is None:
            return []
        return RideEventSerializer(
            events,
            many=True,
            context=self.context,
        ).data


class RideWriteSerializer(serializers.ModelSerializer):
    """Create/update rides using rider and driver primary keys."""

    class Meta:
        model = Ride
        fields = (
            "status",
            "rider",
            "driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
        )

