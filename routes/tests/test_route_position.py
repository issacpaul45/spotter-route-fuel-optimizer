from django.test import SimpleTestCase

from routes.services.route_position import (
    calculate_cumulative_distances,
    haversine_distance,
)


class RoutePositionTests(SimpleTestCase):

    def test_haversine_distance(self):
        distance = haversine_distance(
            34.0536909,
            -118.242766,
            33.4484367,
            -112.074141,
        )

        self.assertGreater(distance, 0)

    def test_cumulative_distances(self):
        coordinates = [
            (-118.242766, 34.0536909),
            (-117.242766, 34.0536909),
            (-116.242766, 34.0536909),
        ]

        result = calculate_cumulative_distances(coordinates)

        self.assertEqual(
            result[0]["distance_miles"],
            0.0,
        )

        self.assertGreater(
            result[1]["distance_miles"],
            result[0]["distance_miles"],
        )

        self.assertGreater(
            result[2]["distance_miles"],
            result[1]["distance_miles"],
        )