import logging
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

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


logger = logging.getLogger(__name__)


def optimize_route(start_location, destination_location):
    total_start = perf_counter()

    logger.info(
        "Starting route optimization: %s -> %s",
        start_location,
        destination_location,
    )

    # ---------------------------------------------------------
    # Geocoding
    # ---------------------------------------------------------
    geocoding_start = perf_counter()

    with ThreadPoolExecutor(max_workers=2) as executor:
        start_future = executor.submit(
            geocode_location,
            start_location,
        )

        destination_future = executor.submit(
            geocode_location,
            destination_location,
        )

        start = start_future.result()
        destination = destination_future.result()

    geocoding_time = perf_counter() - geocoding_start

    logger.info(
        "Geocoding (concurrent): %.2fs",
        geocoding_time,
    )

    # ---------------------------------------------------------
    # Routing
    # ---------------------------------------------------------
    routing_start = perf_counter()

    route = get_route(
        start,
        destination,
    )

    routing_time = perf_counter() - routing_start

    logger.info(
        "Routing: %.2fs",
        routing_time,
    )

    logger.info(
        "Route distance: %.2f miles",
        route["distance"],
    )

    # ---------------------------------------------------------
    # Fuel station lookup
    # ---------------------------------------------------------
    fuel_lookup_start = perf_counter()

    pois = get_fuel_stations(
        route["polyline"],
    )

    fuel_lookup_time = (
        perf_counter() - fuel_lookup_start
    )

    logger.info(
        "Fuel station lookup: %.2fs",
        fuel_lookup_time,
    )

    logger.info(
        "Fuel station POIs returned: %d",
        len(pois),
    )

    # ---------------------------------------------------------
    # Station matching + route positioning
    # ---------------------------------------------------------
    matching_start = perf_counter()

    matches = match_fuel_stations(
        pois,
    )

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
                "opis_id": station.opis_id,
                "distance_miles": distance,
                "price_per_gallon": station.retail_price,
                "latitude": match["latitude"],
                "longitude": match["longitude"],
            }
        )

    stations.sort(
        key=lambda station: station["distance_miles"]
    )

    matching_time = perf_counter() - matching_start

    logger.info(
        "Station matching: %.2fs",
        matching_time,
    )

    logger.info(
        "Matched database stations: %d",
        len(stations),
    )

    # ---------------------------------------------------------
    # Fuel optimization
    # ---------------------------------------------------------
    optimization_start = perf_counter()

    fuel_result = optimize_fuel_stops(
        stations=stations,
        route_distance=route["distance"],
    )

    optimization_time = (
        perf_counter() - optimization_start
    )

    logger.info(
        "Fuel optimization: %.2fs",
        optimization_time,
    )

    logger.info(
        "Fuel stops selected: %d",
        len(fuel_result["stops"]),
    )

    logger.info(
        "Total fuel cost: $%.2f",
        fuel_result["total_cost"],
    )

    # ---------------------------------------------------------
    # Total
    # ---------------------------------------------------------
    total_time = perf_counter() - total_start

    logger.info(
        "Total request time: %.2fs",
        total_time,
    )

    return {
        "route": {
            "distance_miles": round(
                route["distance"],
                2,
            ),
            "duration_seconds": round(
                route["time"],
                2,
            ),
            "geometry": route["geometry"],
        },
        "fuel": {
            "stops": [
                {
                    "name": stop["name"],
                    "distance_miles": round(
                        stop["distance_miles"],
                        2,
                    ),
                    "price_per_gallon": float(
                        stop["price_per_gallon"]
                    ),
                    "gallons_purchased": round(
                        stop["gallons_purchased"],
                        3,
                    ),
                    "cost": round(
                        float(stop["cost"]),
                        2,
                    ),
                }
                for stop in fuel_result["stops"]
            ],
            "total_gallons": round(
                fuel_result["total_gallons"],
                3,
            ),
            "total_cost": round(
                float(fuel_result["total_cost"]),
                2,
            ),
        },
    }