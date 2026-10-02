import logging
import os

import requests


logger = logging.getLogger(__name__)


API_KEY = os.environ["GEOAPIFY_API_KEY"]


class GeoapifyError(Exception):
    """Raised when a Geoapify request fails."""
    pass


def get_route(start, destination):
    url = "https://api.geoapify.com/v1/routing"

    params = {
        "waypoints": (
            f"{start['latitude']},{start['longitude']}"
            f"|"
            f"{destination['latitude']},{destination['longitude']}"
        ),
        "mode": "drive",
        "units": "imperial",
        "details": "polyline6",
        "apiKey": API_KEY,
    }

    logger.info(
        "Requesting route from Geoapify"
    )

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        logger.error(
            "Geoapify routing request failed: status=%s",
            getattr(response, "status_code", None),
        )

        raise GeoapifyError(
            "Unable to retrieve route from routing service."
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error(
            "Geoapify routing response was not valid JSON"
        )

        raise GeoapifyError(
            "Invalid response received from routing service."
        ) from exc

    features = data.get("features", [])

    if not features:
        logger.error(
            "Geoapify routing response contained no route"
        )

        raise GeoapifyError(
            "Routing service returned no route."
        )

    route = features[0]
    properties = route["properties"]

    return {
        "polyline": properties["polyline6"],
        "geometry": route["geometry"],
        "distance": properties["distance"],
        "time": properties["time"],
    }


def get_fuel_stations(polyline):
    url = "https://api.geoapify.com/v2/places"

    params = {
        "apiKey": API_KEY,
    }

    payload = {
        "categories": [
            "service.vehicle.fuel",
        ],
        "filter": {
            "type": "polyline",
            "geometry": polyline,
            "encoding": "polyline6",
            "buffer": 2000,
        },
        "limit": 50,
        "offset": 0,
    }

    logger.info(
        "Requesting fuel stations along route"
    )

    try:
        response = requests.post(
            url,
            params=params,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        logger.error(
            "Geoapify places request failed: status=%s",
            getattr(response, "status_code", None),
        )

        raise GeoapifyError(
            "Unable to retrieve fuel stations from places service."
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error(
            "Geoapify places response was not valid JSON"
        )

        raise GeoapifyError(
            "Invalid response received from places service."
        ) from exc

    features = data.get("features", [])

    logger.info(
        "Geoapify returned %d fuel station POIs",
        len(features),
    )

    return features