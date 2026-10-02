from math import radians, sin, cos, sqrt, atan2

from shapely.geometry import LineString, Point


EARTH_RADIUS_MILES = 3958.7613


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two coordinates.
    Returns miles.
    """

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return EARTH_RADIUS_MILES * c


def flatten_route_geometry(geometry):
    """
    Convert GeoJSON MultiLineString/LineString geometry
    into a single list of [longitude, latitude] coordinates.
    """

    geometry_type = geometry["type"]
    coordinates = geometry["coordinates"]

    if geometry_type == "LineString":
        return coordinates

    if geometry_type == "MultiLineString":
        flattened = []

        for line in coordinates:
            flattened.extend(line)

        return flattened

    raise ValueError(
        f"Unsupported geometry type: {geometry_type}"
    )


def calculate_cumulative_distances(coordinates):
    """
    Calculate cumulative distance along the route.

    Returns:

    [
        {
            "coordinate": [lon, lat],
            "distance_miles": 0.0,
        },
        ...
    ]
    """

    result = []

    cumulative_distance = 0.0

    for index, coordinate in enumerate(coordinates):

        lon, lat = coordinate

        if index > 0:
            previous_lon, previous_lat = coordinates[index - 1]

            cumulative_distance += haversine_distance(
                previous_lat,
                previous_lon,
                lat,
                lon,
            )

        result.append(
            {
                "coordinate": coordinate,
                "distance_miles": cumulative_distance,
            }
        )

    return result


def station_distance_from_start(
    geometry,
    station_latitude,
    station_longitude,
):
    """
    Calculate approximately how many miles along the route
    a fuel station is located.
    """

    coordinates = flatten_route_geometry(geometry)

    cumulative = calculate_cumulative_distances(
        coordinates
    )

    route_line = LineString(coordinates)

    station_point = Point(
        station_longitude,
        station_latitude,
    )

    # Position of the station projected onto the route.
    projected_distance = route_line.project(
        station_point
    )

    # Find the projected point on the route.
    projected_point = route_line.interpolate(
        projected_distance
    )

    # Find the closest route segment.
    closest_segment = None
    closest_distance = float("inf")

    for index in range(len(coordinates) - 1):

        segment = LineString(
            [
                coordinates[index],
                coordinates[index + 1],
            ]
        )

        distance = segment.distance(
            projected_point
        )

        if distance < closest_distance:
            closest_distance = distance
            closest_segment = index

    if closest_segment is None:
        return 0.0

    start_coordinate = coordinates[
        closest_segment
    ]

    end_coordinate = coordinates[
        closest_segment + 1
    ]

    segment_length = haversine_distance(
        start_coordinate[1],
        start_coordinate[0],
        end_coordinate[1],
        end_coordinate[0],
    )

    if segment_length == 0:
        return cumulative[
            closest_segment
        ]["distance_miles"]

    # Determine how far along the segment the
    # projected point is.
    segment = LineString(
        [
            start_coordinate,
            end_coordinate,
        ]
    )

    position_on_segment = segment.project(
        projected_point
    )

    segment_fraction = (
        position_on_segment / segment.length
    )

    distance_from_segment_start = (
        segment_length * segment_fraction
    )

    return (
        cumulative[closest_segment][
            "distance_miles"
        ]
        + distance_from_segment_start
    )