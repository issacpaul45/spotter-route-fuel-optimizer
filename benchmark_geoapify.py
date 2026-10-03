import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["GEOAPIFY_API_KEY"]

START = {"latitude": 34.0522, "longitude": -118.2437}
DESTINATION = {"latitude": 35.0844, "longitude": -106.6504}


def get_route():
    url = "https://api.geoapify.com/v1/routing"

    params = {
        "waypoints": (
            f"{START['latitude']},{START['longitude']}"
            f"|"
            f"{DESTINATION['latitude']},{DESTINATION['longitude']}"
        ),
        "mode": "drive",
        "units": "imperial",
        "details": "polyline6",
        "apiKey": API_KEY,
    }

    start = time.perf_counter()

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    elapsed = time.perf_counter() - start

    response.raise_for_status()

    data = response.json()
    route = data["features"][0]

    return route, elapsed


def get_fuel_stations(polyline):
    url = "https://api.geoapify.com/v2/places"

    params = {
        "apiKey": API_KEY,
    }

    payload = {
        "categories": ["service.vehicle.fuel"],
        "filter": {
            "type": "polyline",
            "geometry": polyline,
            "encoding": "polyline6",
            "buffer": 2000,
        },
        "limit": 50,
        "offset": 0,
    }

    start = time.perf_counter()

    response = requests.post(
        url,
        params=params,
        json=payload,
        timeout=30,
    )

    elapsed = time.perf_counter() - start

    response.raise_for_status()

    data = response.json()

    return data.get("features", []), elapsed


print("\nGeoapify standalone benchmark")
print("=" * 50)

for i in range(5):
    print(f"\nRun {i + 1}")

    try:
        route, routing_time = get_route()

        print(f"Routing:        {routing_time:.2f}s")

        polyline = route["properties"]["polyline6"]

        stations, places_time = get_fuel_stations(polyline)

        print(f"Places:         {places_time:.2f}s")
        print(f"Stations:       {len(stations)}")
        print(f"External total: {routing_time + places_time:.2f}s")

    except Exception as exc:
        print(f"ERROR: {exc}")