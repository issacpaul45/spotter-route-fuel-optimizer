from decimal import Decimal


FUEL_ECONOMY_MPG = 10
MAX_RANGE_MILES = 500
TANK_CAPACITY_GALLONS = MAX_RANGE_MILES / FUEL_ECONOMY_MPG


class FuelOptimizationError(Exception):
    """Raised when the route cannot be completed with the available stations."""
    pass


def optimize_fuel_stops(
    stations,
    route_distance,
    starting_fuel_full=True,
):
    """
    Determine cost-effective fuel stops along a route.

    Assumptions:
    - Vehicle gets 10 MPG.
    - Maximum range is 500 miles.
    - Tank capacity is therefore 50 gallons.
    - Vehicle starts with a full tank by default.
    - Stations must already be ordered by distance from the start.
    """

    if not stations:
        if route_distance <= MAX_RANGE_MILES:
            return {
                "stops": [],
                "total_gallons": 0.0,
                "total_cost": 0.0,
            }

        raise FuelOptimizationError(
            "No fuel stations are available and the route exceeds "
            "the vehicle's 500-mile range."
        )

    stations = sorted(
        stations,
        key=lambda station: station["distance_miles"],
    )

    current_fuel = (
        TANK_CAPACITY_GALLONS
        if starting_fuel_full
        else 0.0
    )

    current_position = 0.0

    stops = []
    total_gallons = 0.0
    total_cost = Decimal("0.00")

    for index, station in enumerate(stations):

        station_position = station["distance_miles"]

        # Ignore stations beyond the destination.
        if station_position >= route_distance:
            break

        distance_to_station = (
            station_position - current_position
        )

        fuel_needed = distance_to_station / FUEL_ECONOMY_MPG

        # We must be able to reach this station.
        if fuel_needed > current_fuel:
            raise FuelOptimizationError(
                f"Cannot reach {station['name']} at "
                f"{station_position:.2f} miles. "
                f"Fuel required: {fuel_needed:.2f} gallons, "
                f"fuel available: {current_fuel:.2f} gallons."
            )

        # Drive to the station.
        current_fuel -= fuel_needed
        current_position = station_position

        distance_to_destination = (
            route_distance - current_position
        )

        destination_fuel_needed = (
            distance_to_destination / FUEL_ECONOMY_MPG
        )

        # Already have enough fuel to reach destination.
        if destination_fuel_needed <= current_fuel:
            break

        current_price = Decimal(
            str(station["price_per_gallon"])
        )

        # Find the FIRST cheaper station that is reachable
        # after refueling at the current station.
        cheaper_station = None

        for future_station in stations[index + 1:]:
            future_position = future_station["distance_miles"]

            if future_position >= route_distance:
                break

            distance_to_future = (
                future_position - current_position
            )

            # Can't reach this station even with a full tank.
            if distance_to_future > MAX_RANGE_MILES:
                break

            future_price = Decimal(
                str(future_station["price_per_gallon"])
            )

            if future_price < current_price:
                cheaper_station = future_station
                break

        if cheaper_station:
            target_distance = (
                cheaper_station["distance_miles"]
                - current_position
            )

            target_fuel = (
                target_distance / FUEL_ECONOMY_MPG
            )

            gallons_to_buy = max(
                0.0,
                target_fuel - current_fuel,
            )

        else:
            # No cheaper station within 500 miles.
            #
            # If destination can be reached with a full tank,
            # only buy what is necessary.
            if distance_to_destination <= MAX_RANGE_MILES:
                target_fuel = destination_fuel_needed

                gallons_to_buy = max(
                    0.0,
                    target_fuel - current_fuel,
                )

            else:
                # Destination is more than 500 miles away.
                # Fill the tank.
                gallons_to_buy = max(
                    0.0,
                    TANK_CAPACITY_GALLONS - current_fuel,
                )

        if gallons_to_buy > 0:
            current_fuel += gallons_to_buy

            cost = (
                Decimal(str(gallons_to_buy))
                * current_price
            )

            total_gallons += gallons_to_buy
            total_cost += cost

            stops.append(
                {
                    "name": station["name"],
                    "distance_miles": round(
                        current_position,
                        2,
                    ),
                    "price_per_gallon": float(
                        current_price
                    ),
                    "gallons_purchased": round(
                        gallons_to_buy,
                        3,
                    ),
                    "cost": float(
                        cost.quantize(
                            Decimal("0.01")
                        )
                    ),
                }
            )

    # After processing all usable stations, check whether
    # the destination is reachable.
    remaining_distance = (
        route_distance - current_position
    )

    remaining_fuel_needed = (
        remaining_distance / FUEL_ECONOMY_MPG
    )

    if remaining_fuel_needed > current_fuel:
        raise FuelOptimizationError(
            "The destination cannot be reached with the "
            "available fuel stations."
        )

    return {
        "stops": stops,
        "total_gallons": round(total_gallons, 3),
        "total_cost": float(
            total_cost.quantize(
                Decimal("0.01")
            )
        ),
    }