from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RouteOptimizationAPITests(APITestCase):

    def test_missing_start_returns_400(self):
        response = self.client.post(
            reverse("route-optimize"),
            {
                "destination": "Phoenix, AZ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("start", response.data)

    def test_missing_destination_returns_400(self):
        response = self.client.post(
            reverse("route-optimize"),
            {
                "start": "Los Angeles, CA",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("destination", response.data)

    def test_blank_start_returns_400(self):
        response = self.client.post(
            reverse("route-optimize"),
            {
                "start": "",
                "destination": "Phoenix, AZ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch("routes.views.optimize_route")
    def test_successful_request_returns_200(
        self,
        mock_optimize_route,
    ):
        mock_optimize_route.return_value = {
            "route": {
                "distance_miles": 373.31,
                "duration_seconds": 19471.68,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [],
                },
            },
            "fuel": {
                "stops": [],
                "total_gallons": 0.0,
                "total_cost": 0.0,
            },
        }

        response = self.client.post(
            reverse("route-optimize"),
            {
                "start": "Los Angeles, CA",
                "destination": "Phoenix, AZ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["route"]["distance_miles"],
            373.31,
        )

        mock_optimize_route.assert_called_once_with(
            start_location="Los Angeles, CA",
            destination_location="Phoenix, AZ",
        )


from routes.services.geocoder import GeocodingError

@patch("routes.views.optimize_route")
def test_invalid_location_returns_400(
    self,
    mock_optimize_route,
):
    mock_optimize_route.side_effect = GeocodingError(
        "Could not find a location for: skjndvsnkv"
    )

    response = self.client.post(
        reverse("route-optimize"),
        {
            "start": "skjndvsnkv",
            "destination": "Albuquerque, NM",
        },
        format="json",
    )

    self.assertEqual(
        response.status_code,
        status.HTTP_400_BAD_REQUEST,
    )

    self.assertEqual(
        response.data["detail"],
        "Could not find a location for: skjndvsnkv",
    )

from routes.services.geoapify import GeoapifyError

@patch("routes.views.optimize_route")
def test_geoapify_failure_returns_502(
    self,
    mock_optimize_route,
):
    mock_optimize_route.side_effect = GeoapifyError(
        "Unable to retrieve route from routing service."
    )

    response = self.client.post(
        reverse("route-optimize"),
        {
            "start": "Los Angeles, CA",
            "destination": "Phoenix, AZ",
        },
        format="json",
    )

    self.assertEqual(
        response.status_code,
        status.HTTP_502_BAD_GATEWAY,
    )