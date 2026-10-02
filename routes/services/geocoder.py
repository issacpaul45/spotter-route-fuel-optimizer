import logging
import os
import re

import requests
from django.core.cache import cache


logger = logging.getLogger(__name__)


API_KEY = os.environ["GEOAPIFY_API_KEY"]
GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"

GEOCODING_CACHE_TIMEOUT = 60 * 60 * 24 * 30


class GeocodingError(Exception):
    """Raised when a location cannot be geocoded."""
    pass


def geocode_location(location):
    normalized_location = location.strip().lower()

    safe_location = re.sub(
        r"[^a-z0-9]+",
        "_",
        normalized_location,
    ).strip("_")

    cache_key = f"geocode:us:{safe_location}"

    cached_result = cache.get(cache_key)

    if cached_result is not None:
        logger.info(
            "Geocoding cache hit: %s",
            location,
        )

        return cached_result

    logger.info(
        "Geocoding location: %s",
        location,
    )

    params = {
        "text": location,
        "filter": "countrycode:us",
        "limit": 1,
        "format": "json",
        "apiKey": API_KEY,
    }

    try:
        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=15,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        logger.error(
            "Geoapify geocoding request failed: "
            "location=%s status=%s",
            location,
            getattr(response, "status_code", None),
        )

        raise GeocodingError(
            f"Unable to geocode location: {location}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error(
            "Geoapify geocoding response was not valid JSON"
        )

        raise GeocodingError(
            f"Invalid response received while geocoding: {location}"
        ) from exc

    results = data.get("results", [])

    if not results:
        logger.warning(
            "No geocoding result found: %s",
            location,
        )

        raise GeocodingError(
            f"Could not find a location for: {location}"
        )

    result = results[0]

    geocoded_location = {
        "latitude": result["lat"],
        "longitude": result["lon"],
        "formatted": result.get(
            "formatted",
            location,
        ),
        "country_code": result.get(
            "country_code",
        ),
    }

    cache.set(
        cache_key,
        geocoded_location,
        timeout=GEOCODING_CACHE_TIMEOUT,
    )

    logger.info(
        "Geocoding completed: %s",
        location,
    )

    return geocoded_location