# import requests


# query = """
# [out:json][timeout:25];

# area["name"="Gila Bend"]["boundary"="administrative"]->.searchArea;

# (
#     nwr
#         ["amenity"="fuel"]
#         ["name"~"PILOT",i]
#         (area.searchArea);
# );

# out center tags;
# """

# url = "https://overpass.private.coffee/api/interpreter"

# headers = {
#     "User-Agent": "SpotterFuelAssessment/1.0"
# }

# response = requests.post(
#     url,
#     data={"data": query},
#     headers=headers,
#     timeout=30,
# )

# print("Status:", response.status_code)
# print("Content-Type:", response.headers.get("content-type"))
# print(response.text[:2000])

# response.raise_for_status()

# data = response.json()

# print("Results:", len(data["elements"]))

# for element in data["elements"]:
#     tags = element.get("tags", {})

#     if element["type"] == "node":
#         latitude = element["lat"]
#         longitude = element["lon"]
#     else:
#         center = element.get("center", {})
#         latitude = center.get("lat")
#         longitude = center.get("lon")

#     print()
#     print("OSM ID:", element["id"])
#     print("Name:", tags.get("name"))
#     print("Brand:", tags.get("brand"))
#     print("Operator:", tags.get("operator"))
#     print("City:", tags.get("addr:city"))
#     print("State:", tags.get("addr:state"))
#     print("Latitude:", latitude)
#     print("Longitude:", longitude)

# import requests


# stations = [
#     ("7", "I-44, EXIT 283 & US-69", "Big Cabin", "OK"),
#     ("9", "I-94, EXIT 143 & US-12 & SR-21", "Tomah", "WI"),
#     ("20", "I-8, EXIT 119 & SR-85", "Gila Bend", "AZ"),
#     ("28", "I-540, EXIT 12 & US-71", "Fort Smith", "AR"),
#     ("35", "US-46", "Columbia", "NJ"),
#     ("36", "I-81, EXIT 273 & SR-703/SR-292", "Mount Jackson", "VA"),
#     ("44", "I-35, EXIT 271", "Jarrell", "TX"),
#     ("46", "I-85, EXIT 22 & CR-138", "Shorter", "AL"),
#     ("49", "I-65, EXIT 50 & US-50 & US-31", "Seymour", "IN"),
#     ("50", "I-29 & I-80, EXIT 3", "Council Bluffs", "IA"),
# ]


# url = "https://geocoding.geo.census.gov/geocoder/locations/address"

# for opis_id, address, city, state in stations:
#     params = {
#         "street": address,
#         "city": city,
#         "state": state,
#         "benchmark": "Public_AR_Current",
#         "format": "json",
#     }

#     response = requests.get(
#         url,
#         params=params,
#         timeout=15,
#     )

#     data = response.json()

#     matches = data["result"]["addressMatches"]

#     print("=" * 70)
#     print(f"ID:      {opis_id}")
#     print(f"Address: {address}")
#     print(f"City:    {city}, {state}")
#     print(f"Matches: {len(matches)}")

#     if matches:
#         match = matches[0]

#         coordinates = match["coordinates"]

#         print("Matched:", match["matchedAddress"])
#         print("Longitude:", coordinates["x"])
#         print("Latitude:", coordinates["y"])


# import os
# import requests


# API_KEY = os.getenv("GEOAPIFY_API_KEY")

# if not API_KEY:
#     raise RuntimeError(
#         "GEOAPIFY_API_KEY is not set. "
#         "Run: export GEOAPIFY_API_KEY='YOUR_API_KEY'"
#     )


# stations = [
#     ("7", "I-44, EXIT 283 & US-69", "Big Cabin", "OK"),
#     ("9", "I-94, EXIT 143 & US-12 & SR-21", "Tomah", "WI"),
#     ("20", "I-8, EXIT 119 & SR-85", "Gila Bend", "AZ"),
#     ("28", "I-540, EXIT 12 & US-71", "Fort Smith", "AR"),
#     ("35", "US-46", "Columbia", "NJ"),
#     ("36", "I-81, EXIT 273 & SR-703/SR-292", "Mount Jackson", "VA"),
#     ("44", "I-35, EXIT 271", "Jarrell", "TX"),
#     ("46", "I-85, EXIT 22 & CR-138", "Shorter", "AL"),
#     ("49", "I-65, EXIT 50 & US-50 & US-31", "Seymour", "IN"),
#     ("50", "I-29 & I-80, EXIT 3", "Council Bluffs", "IA"),
# ]


# url = "https://api.geoapify.com/v1/geocode/search"


# for opis_id, address, city, state in stations:

#     search_text = f"{address}, {city}, {state}, USA"

#     params = {
#         "text": search_text,
#         "filter": "countrycode:us",
#         "limit": 5,
#         "format": "json",
#         "apiKey": API_KEY,
#     }

#     try:
#         response = requests.get(
#             url,
#             params=params,
#             timeout=15,
#         )

#         response.raise_for_status()

#         data = response.json()

#     except requests.RequestException as exc:
#         print("=" * 70)
#         print(f"ID:      {opis_id}")
#         print(f"Query:   {search_text}")
#         print(f"ERROR:   {exc}")
#         continue

#     results = data.get("results", [])

#     print("=" * 70)
#     print(f"ID:      {opis_id}")
#     print(f"Query:   {search_text}")
#     print(f"Matches: {len(results)}")

#     for result in results:

#         print(
#             f"  Name:    {result.get('name')}"
#         )

#         print(
#             f"  Address: {result.get('formatted')}"
#         )

#         print(
#             f"  Lat:     {result.get('lat')}"
#         )

#         print(
#             f"  Lon:     {result.get('lon')}"
#         )

#         print(
#             f"  Type:    {result.get('result_type')}"
#         )

import os
import csv
import requests


API_KEY = os.getenv("GEOAPIFY_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEOAPIFY_API_KEY is not set.\n"
        "Run:\n"
        'export GEOAPIFY_API_KEY="YOUR_REAL_API_KEY"'
    )


CSV_FILE = "data/fuel-prices-for-be-assessment.csv"

URL = "https://api.geoapify.com/v1/geocode/search"

MAX_STATIONS = 10


with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:

    reader = csv.DictReader(file)

    seen_ids = set()
    tested = 0

    for row in reader:

        opis_id = row["OPIS Truckstop ID"]

        # Skip duplicate OPIS IDs
        if opis_id in seen_ids:
            continue

        seen_ids.add(opis_id)

        if tested >= MAX_STATIONS:
            break

        tested += 1

        name = row["Truckstop Name"].strip()
        address = row["Address"].strip()
        city = row["City"].strip()
        state = row["State"].strip()

        # Search using the actual truck-stop name.
        search_text = f"{name}, {city}, {state}, USA"

        params = {
            "text": search_text,
            "filter": "countrycode:us",
            "limit": 5,
            "format": "json",
            "apiKey": API_KEY,
        }

        print("=" * 80)

        print(f"OPIS ID:          {opis_id}")
        print(f"CSV Name:         {name}")
        print(f"CSV Address:      {address}")
        print(f"CSV Location:     {city}, {state}")
        print(f"Geoapify Query:   {search_text}")

        try:

            response = requests.get(
                URL,
                params=params,
                timeout=15,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as exc:

            print(f"ERROR: {exc}")
            continue

        results = data.get("results", [])

        print(f"Matches:          {len(results)}")

        if not results:
            print("No results")
            continue

        for result_number, result in enumerate(results, start=1):

            print()
            print(f"--- Result #{result_number} ---")

            print(
                "Name:        ",
                result.get("name")
            )

            print(
                "Address:     ",
                result.get("formatted")
            )

            print(
                "Latitude:    ",
                result.get("lat")
            )

            print(
                "Longitude:   ",
                result.get("lon")
            )

            print(
                "Type:        ",
                result.get("result_type")
            )

            print(
                "Category:    ",
                result.get("category")
            )