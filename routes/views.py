
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from routes.serializers import RouteOptimizationSerializer
from routes.services.geocoder import GeocodingError
from routes.services.geoapify import GeoapifyError
from routes.services.optimizer import FuelOptimizationError
from routes.services.route_optimizer import optimize_route


class RouteOptimizationView(CreateAPIView):
    serializer_class = RouteOptimizationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            result = optimize_route(
                start_location=serializer.validated_data[
                    "start"
                ],
                destination_location=serializer.validated_data[
                    "destination"
                ],
            )

        except GeocodingError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except FuelOptimizationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except GeoapifyError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )