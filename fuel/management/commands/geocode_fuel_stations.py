import os
import time

import requests

from django.core.management.base import BaseCommand

from fuel.models import FuelStation


GEOAPIFY_URL = "https://api.geoapify.com/v1/geocode/search"


class Command(BaseCommand):
    help = "Geocode fuel stations using Geoapify"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of stations to process. 0 = all.",
        )

        parser.add_argument(
            "--delay",
            type=float,
            default=0.35,
            help="Delay between API requests in seconds.",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-geocode stations that already have coordinates.",
        )

    def handle(self, *args, **options):

        api_key = os.getenv("GEOAPIFY_API_KEY")

        if not api_key:
            self.stderr.write(
                self.style.ERROR(
                    "GEOAPIFY_API_KEY environment variable is not set."
                )
            )
            return

        limit = options["limit"]
        delay = options["delay"]
        force = options["force"]

        queryset = FuelStation.objects.all().order_by("id")

        if not force:
            queryset = queryset.filter(
                latitude__isnull=True,
                longitude__isnull=True,
            )

        if limit:
            queryset = queryset[:limit]

        total = queryset.count()

        self.stdout.write(
            f"Stations to process: {total}"
        )

        success_count = 0
        failed_count = 0
        skipped_count = 0

        session = requests.Session()

        session.headers.update(
            {
                "User-Agent": "SpotterFuelAssessment/1.0",
            }
        )

        for index, station in enumerate(queryset, start=1):

            self.stdout.write(
                f"[{index}/{total}] "
                f"{station.opis_id} - "
                f"{station.name} - "
                f"{station.city}, {station.state}"
            )

            # Search using station name + original address + city/state.
            search_text = (
                f"{station.name}, "
                f"{station.address}, "
                f"{station.city}, "
                f"{station.state}, USA"
            )

            params = {
                "text": search_text,
                "filter": "countrycode:us",
                "type": "amenity",
                "limit": 5,
                "format": "json",
                "apiKey": api_key,
            }

            try:
                response = session.get(
                    GEOAPIFY_URL,
                    params=params,
                    timeout=15,
                )

                response.raise_for_status()

                data = response.json()

            except requests.RequestException as exc:

                failed_count += 1

                self.stderr.write(
                    self.style.WARNING(
                        f"  API error: {exc}"
                    )
                )

                time.sleep(delay)

                continue

            results = data.get("results", [])

            if not results:

                # Second attempt:
                # Remove the unusual highway-exit address.
                fallback_query = (
                    f"{station.name}, "
                    f"{station.city}, "
                    f"{station.state}, USA"
                )

                fallback_params = {
                    "text": fallback_query,
                    "filter": "countrycode:us",
                    "type": "amenity",
                    "limit": 5,
                    "format": "json",
                    "apiKey": api_key,
                }

                try:

                    response = session.get(
                        GEOAPIFY_URL,
                        params=fallback_params,
                        timeout=15,
                    )

                    response.raise_for_status()

                    data = response.json()

                    results = data.get("results", [])

                except requests.RequestException as exc:

                    failed_count += 1

                    self.stderr.write(
                        self.style.WARNING(
                            f"  Fallback API error: {exc}"
                        )
                    )

                    time.sleep(delay)

                    continue

            if not results:

                failed_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        "  No suitable result found"
                    )
                )

                time.sleep(delay)

                continue

            # Select the best result.
            result = self.select_best_result(
                results=results,
                station=station,
            )

            if result is None:

                skipped_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        "  No trustworthy result"
                    )
                )

                time.sleep(delay)

                continue

            latitude = result.get("lat")
            longitude = result.get("lon")

            if latitude is None or longitude is None:

                failed_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        "  Result has no coordinates"
                    )
                )

                time.sleep(delay)

                continue

            station.latitude = latitude
            station.longitude = longitude

            station.save(
                update_fields=[
                    "latitude",
                    "longitude",
                ]
            )

            success_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {latitude}, {longitude}"
                )
            )

            time.sleep(delay)

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successful: {success_count}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Failed:     {failed_count}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Skipped:    {skipped_count}"
            )
        )
        self.stdout.write("=" * 60)

    def select_best_result(self, results, station):
        """
        Select the most plausible Geoapify result.

        Preference:
        1. Result is an amenity.
        2. Result is in the correct state.
        3. Result is in the correct city.
        4. Higher confidence.
        """

        station_city = station.city.lower().strip()
        station_state = station.state.lower().strip()

        candidates = []

        for result in results:

            result_type = (
                result.get("result_type") or ""
            ).lower()

            result_city = (
                result.get("city") or ""
            ).lower().strip()

            result_state = (
                result.get("state_code")
                or result.get("state")
                or ""
            ).lower().strip()

            confidence = (
                result.get("rank", {})
                .get("confidence", 0)
            )

            score = 0

            # Strongly prefer actual POIs/amenities.
            if result_type == "amenity":
                score += 100

            # Correct state.
            if result_state == station_state:
                score += 50

            # Correct city.
            if result_city == station_city:
                score += 50

            # Prefer higher Geoapify confidence.
            score += confidence * 10

            candidates.append(
                (
                    score,
                    result,
                )
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        best_score, best_result = candidates[0]

        # Don't accept obvious garbage results.
        if best_score < 50:
            return None

        return best_result