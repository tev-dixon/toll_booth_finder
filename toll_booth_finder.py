# thomas dixon
# teddixon@umich.edu

import os
import requests
from dotenv import load_dotenv
from haversine import haversine
import webbrowser
import math

load_dotenv()

def get_toll_booths_along_route(api_key, start_point, destinations, radius=5000, sampling_interval=50):
    # Get the route from the Directions API
    waypoints = '|'.join([f'via:{lat},{lng}' for lat, lng in destinations])
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_point[0]},{start_point[1]}&destination={destinations[-1][0]},{destinations[-1][1]}&waypoints={waypoints}&key={api_key}"
    directions_response = requests.get(directions_url)
    directions_data = directions_response.json()

    if directions_data["status"] != "OK":
        print(f"Error: {directions_data['status']}")
        return []

    # Extract the route's polyline
    polyline = directions_data["routes"][0]["overview_polyline"]["points"]

    # Decode the polyline into a list of coordinates
    coordinates = decode_polyline(polyline)

    # Sample the coordinates at regular intervals
    #print(get_distance(start_point, destinations[-1], api_key))
    samp = 1/(get_distance(start_point, destinations[-1], api_key)/1000)*3030/len(destinations)
    sampled_coordinates = coordinates[::int(math.ceil(samp))]
    print("Sampling at rate: " + str(samp) + " rounded to " + str(math.ceil(samp)))
    print("Note that if sample rate is far below 1, the polyline may be underdefined")

    toll_booths = []

    # Search for toll booths along the route
    for coord in sampled_coordinates:
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
            toll_booths.extend(response_data["results"])
            print("found!")

    # Remove duplicate toll booths
    unique_toll_booths = {booth['place_id']: booth for booth in toll_booths}.values()

    print_toll_booths(unique_toll_booths)

    return unique_toll_booths

def get_distance(origin, destination, api_key):
    ori = ','.join(map(str, origin))
    dst = ','.join(map(str, destination))
    #print(ori)
    #print(dst)
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={ori}&destinations={dst}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        distance = data["rows"][0]["elements"][0]["distance"]["value"]
        return distance
    else:
        print(f"Error: {data['status']}")
        return None

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

    while (True):
        pt = get_user_input("What toll booth location would you like to open?\nenter a number or 'A' for all\ne to exit\n")
        if (pt == "A" or pt == "a"):
            for i, booth in enumerate(toll_booths, start=1):
                address = booth.get("vicinity", "No address available")
                open_google_maps(address)
            break
        if (pt == "e"):
            break
        else:
            num = 0
            try:
                num = int(pt)
            except ValueError:
                print(f'Error: Cannot convert "{num}" to an integer... try again.\n')
                continue
            if (int(pt) < 1 or int(pt) > len(toll_booths)):
                print("Error: index out of bounds... try again.\n")
                continue

            toll_booths_list = list(toll_booths)
            booth = toll_booths_list[num-1]

            address = booth.get("vicinity", "No address available")
            open_google_maps(address)

    
def open_google_maps(location):
    url = "https://www.google.com/maps/search/?api=1&query=" + location.replace(" ", "+")
    webbrowser.open_new_tab(url)

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

def get_city_coordinates(api_key, city_name):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        print(f"Error: {data['status']}")
        return None

    location = data["results"][0]["geometry"]["location"]
    return (location["lat"], location["lng"])



api_key = os.getenv("GOOGLE_MAPS_API_KEY")

def get_user_input(prompt):
    user_input = input(prompt)
    return user_input

pointlist = []
coordlist = []

stpt = ""
stcc = None
while (True):
    stpt = get_user_input("Enter Starting City: ")
    city_coordinates = get_city_coordinates(api_key, stpt)
    if (city_coordinates == None):
        print("Error: no such city exists!\n")
    else:
        print("Success! Point found. Coordinates are: " + f"({str(city_coordinates[0])}, {str(city_coordinates[1])})" + "\n")
        stcc = city_coordinates
        break

edpt = ""
edcc = None
while (True):
    edpt = get_user_input("Enter Destination City: ")
    city_coordinates = get_city_coordinates(api_key, edpt)
    if (city_coordinates == None):
        print("Error: no such city exists!\n")
    else:
        print("Success! Point found. Coordinates are: " + f"({str(city_coordinates[0])}, {str(city_coordinates[1])})" + "\n")
        edcc = city_coordinates
        break

while (True):
    pt = get_user_input("Enter Intermediate Points (city names) enter e to stop: ")
    if (pt == "e"):
        break
    city_coordinates = get_city_coordinates(api_key, pt)
    if (city_coordinates == None):
        print("Error: point ignored, no such city exists!\n")
    else:
        print("Success! Point found. Coordinates are: " + f"({str(city_coordinates[0])}, {str(city_coordinates[1])})" + "\n")
        coordlist.append(city_coordinates)

coordlist.append(edcc)

print("Generating...\nthis should not take about 5 seconds per 60 kilometers of travel and 1.5x (stacking) longer per additional intermediate waypoint...")
toll_booths = get_toll_booths_along_route(api_key, stcc, coordlist)