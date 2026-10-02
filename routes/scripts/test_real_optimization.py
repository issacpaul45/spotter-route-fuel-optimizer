# import os
# import django

# os.environ.setdefault(
#     "DJANGO_SETTINGS_MODULE",
#     "config.settings",
# )

# django.setup()

# from routes.services.geoapify_test import (
#     get_route,
#     get_fuel_stations,
# )

# from routes.services.fuel_matcher import (
#     match_fuel_stations,
# )

# from routes.services.route_position import (
#     station_distance_from_start,
# )

# from routes.services.optimizer import (
#     optimize_fuel_stops,
# )


# # 1. Get route
# route = get_route()


# # 2. Find fuel stations along route
# pois = get_fuel_stations(
#     route["polyline"]
# )


# # 3. Match Geoapify stations
# #    against our PostgreSQL price data
# matches = match_fuel_stations(pois)


# # 4. Calculate each station's position
# #    along the route
# stations = []

# for match in matches:

#     station = match["station"]

#     distance = station_distance_from_start(
#         route["geometry"],
#         match["latitude"],
#         match["longitude"],
#     )

#     stations.append(
#         {
#             "name": station.name,
#             "distance_miles": distance,
#             "price_per_gallon": station.retail_price,
#             "latitude": match["latitude"],
#             "longitude": match["longitude"],
#             "opis_id": station.opis_id,
#         }
#     )


# # 5. Sort by position along route
# stations.sort(
#     key=lambda station: station["distance_miles"]
# )


# print("\n=== CANDIDATE STATIONS ===")

# for station in stations:
#     print(
#         f"{station['name']} | "
#         f"{station['distance_miles']:.2f} miles | "
#         f"${station['price_per_gallon']}"
#     )


# # 6. Run optimizer
# result = optimize_fuel_stops(
#     stations=stations,
#     route_distance=route["distance"],
# )


# print("\n=== OPTIMAL FUEL STOPS ===")

# for stop in result["stops"]:
#     print(
#         f"{stop['name']} | "
#         f"{stop['distance_miles']} miles | "
#         f"${stop['price_per_gallon']}/gal | "
#         f"{stop['gallons_purchased']} gallons | "
#         f"${stop['cost']}"
#     )


# print("\n=== TOTAL ===")

# print(
#     f"Fuel purchased: "
#     f"{result['total_gallons']} gallons"
# )

# print(
#     f"Fuel cost: "
#     f"${result['total_cost']}"
# )

import os

import django


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()


from routes.services.geocoder import (
    geocode_location,
)

from routes.services.geoapify import (
    get_route,
    get_fuel_stations,
)

from routes.services.fuel_matcher import (
    match_fuel_stations,
)

from routes.services.route_position import (
    station_distance_from_start,
)

from routes.services.optimizer import (
    optimize_fuel_stops,
)


# ---------------------------------------------------------
# 1. Geocode locations
# ---------------------------------------------------------

start = geocode_location(
    "Los Angeles, CA"
)

destination = geocode_location(
    "Phoenix, AZ"
)


print("\n=== LOCATIONS ===")

print(
    f"Start: "
    f"{start['formatted']}"
)

print(
    f"Start coordinates: "
    f"{start['latitude']}, "
    f"{start['longitude']}"
)

print(
    f"Destination: "
    f"{destination['formatted']}"
)

print(
    f"Destination coordinates: "
    f"{destination['latitude']}, "
    f"{destination['longitude']}"
)


# ---------------------------------------------------------
# 2. Get route
# ---------------------------------------------------------

route = get_route(
    start,
    destination,
)


# ---------------------------------------------------------
# 3. Find fuel stations along route
# ---------------------------------------------------------

pois = get_fuel_stations(
    route["polyline"]
)


# ---------------------------------------------------------
# 4. Match Geoapify stations against our database
# ---------------------------------------------------------

matches = match_fuel_stations(
    pois
)


# ---------------------------------------------------------
# 5. Calculate each station's position on route
# ---------------------------------------------------------

stations = []

for match in matches:

    station = match["station"]

    distance = station_distance_from_start(
        route["geometry"],
        match["latitude"],
        match["longitude"],
    )

    stations.append(
        {
            "name": station.name,
            "distance_miles": distance,
            "price_per_gallon": station.retail_price,
            "latitude": match["latitude"],
            "longitude": match["longitude"],
            "opis_id": station.opis_id,
        }
    )


# ---------------------------------------------------------
# 6. Sort stations by distance
# ---------------------------------------------------------

stations.sort(
    key=lambda station: station["distance_miles"]
)


print("\n=== CANDIDATE STATIONS ===")

for station in stations:

    print(
        f"{station['name']} | "
        f"{station['distance_miles']:.2f} miles | "
        f"${station['price_per_gallon']}"
    )


# ---------------------------------------------------------
# 7. Optimize fuel stops
# ---------------------------------------------------------

result = optimize_fuel_stops(
    stations=stations,
    route_distance=route["distance"],
)


# ---------------------------------------------------------
# 8. Display optimal stops
# ---------------------------------------------------------

print("\n=== OPTIMAL FUEL STOPS ===")

for stop in result["stops"]:

    print(
        f"{stop['name']} | "
        f"{stop['distance_miles']} miles | "
        f"${stop['price_per_gallon']}/gal | "
        f"{stop['gallons_purchased']} gallons | "
        f"${stop['cost']}"
    )


# ---------------------------------------------------------
# 9. Display totals
# ---------------------------------------------------------

print("\n=== TOTAL ===")

print(
    f"Fuel purchased: "
    f"{result['total_gallons']} gallons"
)

print(
    f"Fuel cost: "
    f"${result['total_cost']}"
)