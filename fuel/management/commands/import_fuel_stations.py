import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from fuel.models import FuelStation


class Command(BaseCommand):
    help = "Import fuel stations from the assessment CSV"

    def handle(self, *args, **options):
        csv_path = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "fuel-prices-for-be-assessment.csv"
        )

        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"CSV file not found: {csv_path}"
                )
            )
            return

        stations = []

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                stations.append(
                    FuelStation(
                        opis_id=int(row["OPIS Truckstop ID"]),
                        name=row["Truckstop Name"].strip(),
                        address=row["Address"].strip(),
                        city=row["City"].strip(),
                        state=row["State"].strip(),
                        rack_id=int(row["Rack ID"]),
                        retail_price=row["Retail Price"],
                    )
                )

        FuelStation.objects.bulk_create(
            stations,
            batch_size=500,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(stations)} fuel stations."
            )
        )