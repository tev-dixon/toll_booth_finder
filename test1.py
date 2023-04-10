import os
import requests
from dotenv import load_dotenv
from haversine import haversine
import webbrowser
import math
load_dotenv()

def find_nearest_toll_booth(api_key: str, latitude: float, longitude: float, radius: int = 500) -> dict:
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "key": api_key,
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": "toll booth"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results")

        if results:
            nearest_toll_booth = results[0]
            print("located booth")
            return nearest_toll_booth
        else:
            print("No toll booths found within the specified radius.")
    else:
        print(f"Request failed with status code {response.status_code}")

    return None

def print_toll_booth_info(toll_booth: dict):
    name = toll_booth.get("name")
    lat = toll_booth["geometry"]["location"]["lat"]
    lng = toll_booth["geometry"]["location"]["lng"]

    print(f"Name: {name}")
    print(f"Coordinates: ({lat}, {lng})")

def get_toll_booths_along_route(api_key, slatitude, slongitude, elatitude, elongitude, count, toll_booths = [], radius=1000):
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={slatitude},{slongitude}&destination={elatitude},{elongitude}&key={api_key}"
    directions_response = requests.get(directions_url)
    directions_data = directions_response.json()

    if directions_data["status"] != "OK":
        print(f"Error: {directions_data['status']}")
        return []

    # Extract the route's polyline
    polyline = directions_data["routes"][0]["overview_polyline"]["points"]

    # Decode the polyline into a list of coordinates
    coordinates = decode_polyline(polyline)

    # Sample the coordinates at decreasing intervals
    found = 0
    samp = 200

    toll_booths_dict = {booth['place_id']: booth for booth in toll_booths}
    unique_toll_booths = set(toll_booths_dict.keys())

    unique_toll_booths = set(booth['place_id'] for booth in toll_booths)
    visited_coordinates = []

    while found > 4:
        samp /= 2

        sampled_coordinates = coordinates[::int(math.ceil(samp))]
        for coord in sampled_coordinates:
            if coord in visited_coordinates:
                continue
            visited_coordinates.append(coord)

            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

            params = {
                "key": api_key,
                "location": f"{coord[0]},{coord[1]}",
                "radius": radius,
                "keyword": "toll booth"
            }

            response = requests.get(url, params=params)
            response_data = response.json()

            if response_data["status"] == "OK":
                for booth in response_data["results"]:
                    if booth['place_id'] not in unique_toll_booths:
                        unique_toll_booths.add(booth['place_id'])
                        toll_booths_dict[booth['place_id']] = booth

            found = len(toll_booths_dict)
            print("found: " + str(found))

            if found > 4:
                break

    return list(toll_booths_dict.values())

def print_toll_booths(toll_booths):
    if not toll_booths:
        print("No toll booths found along the route.")
        return

    print(f"Found {len(toll_booths)} toll booths along the route:")
    for i, booth in enumerate(toll_booths, start=1):
        name = booth.get("name", "Unknown")
        address = booth.get("vicinity", "No address available")
        lat = booth["geometry"]["location"]["lat"]
        lng = booth["geometry"]["location"]["lng"]
        print(f"{i}. {name}\n   Address: {address}\n   Latitude: {lat}\n   Longitude: {lng}\n")

def decode_polyline(polyline_str):
    index, lat, lng = 0, 0, 0
    coordinates = []

    while index < len(polyline_str):
        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if not b >= 0x20:
                break
        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat

        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if not b >= 0x20:
                break
        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng

        coordinates.append((lat * 1e-5, lng * 1e-5))

    return coordinates





api_key = os.getenv("GOOGLE_MAPS_API_KEY")
slatitude = 40.00908789510346
slongitude = -83.03518980657284
elatitude = 40.708045217738324
elongitude = -74.07159136350992
count = 4
start_nearest_tb = find_nearest_toll_booth(api_key, slatitude, slongitude)
end_nearest_tb = find_nearest_toll_booth(api_key, elatitude, elongitude)

toll_booths = []
if (start_nearest_tb is not None):
    count-=1
    toll_booths.append(start_nearest_tb)

if (end_nearest_tb is not None):
    count-=1
    toll_booths.append(end_nearest_tb)

uniquetb = get_toll_booths_along_route(api_key, slatitude, slongitude, elatitude, elongitude, 4-count, toll_booths)

for booth in uniquetb:
    if booth is None:
        break
    toll_booths.append(booth)

print_toll_booths(toll_booths)