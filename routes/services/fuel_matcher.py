import re

from fuel.models import FuelStation


def normalize_name(name):
    if not name:
        return ""

    name = str(name)
    name = name.upper()

    # Remove common punctuation
    name = re.sub(r"[^A-Z0-9\s]", " ", name)

    # Normalize whitespace
    name = re.sub(r"\s+", " ", name).strip()

    # Remove common business suffixes
    name = name.replace(" TRAVEL CENTER", "")
    name = name.replace(" TRAVEL STOP", "")
    name = name.replace(" TRUCK STOP", "")

    return name


def normalize_city(city):
    if not city:
        return ""

    return re.sub(r"[^A-Z0-9]", "", city.upper())


def normalize_state(state):
    if not state:
        return ""

    state = state.upper().strip()

    state_mapping = {
        "CALIFORNIA": "CA",
        "ARIZONA": "AZ",
        "TEXAS": "TX",
        "OKLAHOMA": "OK",
        "FLORIDA": "FL",
        "IOWA": "IA",
        "INDIANA": "IN",
        "WISCONSIN": "WI",
        "ALABAMA": "AL",
        "NEW JERSEY": "NJ",
        "VIRGINIA": "VA",
    }

    return state_mapping.get(state, state)


def match_station(poi):
    """
    Match a Geoapify fuel POI against our PostgreSQL
    FuelStation dataset.
    """

    properties = poi["properties"]

    poi_name = normalize_name(properties.get("name"))
    poi_city = normalize_city(properties.get("city"))
    poi_state = normalize_state(properties.get("state"))

    if not poi_city or not poi_state:
        return None

    stations = FuelStation.objects.filter(
        state=poi_state,
        city__iexact=properties.get("city", ""),
    )

    if not stations.exists():
        return None

    # Try name matching
    for station in stations:
        station_name = normalize_name(station.name)

        if not station_name:
            continue

        if (
            station_name in poi_name
            or poi_name in station_name
        ):
            return station

    return None


def match_fuel_stations(pois):
    matches = []

    seen_ids = set()

    for poi in pois:
        station = match_station(poi)

        if not station:
            continue

        if station.id in seen_ids:
            continue

        properties = poi["properties"]

        matches.append(
            {
                "station": station,
                "latitude": properties.get("lat"),
                "longitude": properties.get("lon"),
            }
        )

        seen_ids.add(station.id)

    return matches