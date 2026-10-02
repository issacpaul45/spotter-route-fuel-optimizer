from routes.services.optimizer import (
    optimize_fuel_stops,
)


stations = [
    {
        "name": "Station A",
        "distance_miles": 400,
        "price_per_gallon": 4.00,
    },
    {
        "name": "Station B",
        "distance_miles": 600,
        "price_per_gallon": 3.00,
    },
    {
        "name": "Station C",
        "distance_miles": 750,
        "price_per_gallon": 4.50,
    },
]


route_distance = 900


result = optimize_fuel_stops(
    stations,
    route_distance,
)


print("\n=== FUEL OPTIMIZATION ===")

for stop in result["stops"]:
    print(
        f"{stop['name']} | "
        f"{stop['distance_miles']} miles | "
        f"${stop['price_per_gallon']}/gal | "
        f"{stop['gallons_purchased']} gallons | "
        f"${stop['cost']}"
    )

print(
    f"\nTotal gallons: "
    f"{result['total_gallons']}"
)

print(
    f"Total cost: "
    f"${result['total_cost']}"
)