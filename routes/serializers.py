from rest_framework import serializers


from rest_framework import serializers


class RouteOptimizationSerializer(serializers.Serializer):
    start = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    destination = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    def validate_start(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "Start location must contain at least 2 characters."
            )

        return value

    def validate_destination(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "Destination must contain at least 2 characters."
            )

        return value