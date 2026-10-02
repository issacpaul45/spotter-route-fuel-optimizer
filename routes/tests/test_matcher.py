from decimal import Decimal

from django.test import TestCase

from fuel.models import FuelStation
from routes.services.fuel_matcher import match_station


class FuelMatcherTests(TestCase):

    def setUp(self):
        self.station = FuelStation.objects.create(
            opis_id=999999,
            name="PILOT TRAVEL CENTER #328",
            address="I-10",
            city="Quartzsite",
            state="AZ",
            rack_id=1,
            retail_price=Decimal("3.959"),
        )

    def test_matches_station_by_name_city_and_state(self):
        poi = {
            "properties": {
                "name": "Pilot Travel Center",
                "city": "Quartzsite",
                "state": "AZ",
            }
        }

        result = match_station(poi)

        self.assertEqual(result, self.station)

    def test_returns_none_for_unknown_city(self):
        poi = {
            "properties": {
                "name": "Pilot Travel Center",
                "city": "Phoenix",
                "state": "AZ",
            }
        }

        result = match_station(poi)

        self.assertIsNone(result)