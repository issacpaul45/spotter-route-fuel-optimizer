from routes.services.geocoder import (
    geocode_location,
)


locations = [
    "Los Angeles, CA",
    "Phoenix, AZ",
]


for location in locations:

    result = geocode_location(
        location
    )

    print("\n=== GEOCODE ===")

    print(
        f"Input: {location}"
    )

    print(
        f"Latitude: {result['latitude']}"
    )

    print(
        f"Longitude: {result['longitude']}"
    )

    print(
        f"Formatted: {result['formatted']}"
    )

    print(
        f"Country: {result['country_code']}"
    )