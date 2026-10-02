from django.test import SimpleTestCase

from routes.serializers import RouteOptimizationSerializer


class RouteOptimizationSerializerTests(SimpleTestCase):

    def test_valid_locations(self):
        serializer = RouteOptimizationSerializer(
            data={
                "start": "Los Angeles, CA",
                "destination": "Phoenix, AZ",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["start"],
            "Los Angeles, CA",
        )

    def test_start_is_required(self):
        serializer = RouteOptimizationSerializer(
            data={
                "destination": "Phoenix, AZ",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("start", serializer.errors)

    def test_destination_is_required(self):
        serializer = RouteOptimizationSerializer(
            data={
                "start": "Los Angeles, CA",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("destination", serializer.errors)

    def test_blank_start_is_rejected(self):
        serializer = RouteOptimizationSerializer(
            data={
                "start": "",
                "destination": "Phoenix, AZ",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("start", serializer.errors)

    def test_short_start_is_rejected(self):
        serializer = RouteOptimizationSerializer(
            data={
                "start": "A",
                "destination": "Phoenix, AZ",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("start", serializer.errors)