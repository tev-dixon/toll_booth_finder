# thomas dixon
# teddixon@umich.edu

import os
import requests
from dotenv import load_dotenv
from haversine import haversine
import webbrowser
import math

load_dotenv()

class boothdata:
    def __init__(self, name = "Null", lat = -1.0, lon = -1.0, valid = False):
        self.name = name
        self.lon = lat
        self.lat = lon
        self.valid = valid

class coords:
    def __init__(self, lat = -1.0, lon = -1.0, valid = False):
        self.lon = lat
        self.lat = lon
        self.valid = valid


def find_nearest_toll_booth(api_key: str, latitude: float, longitude: float, radius: int = 1500) -> boothdata:
    #build URL
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": "toll booth"
    }

    #request using URL from API
    response = requests.get(url, params=params)

    #check valid response and check data
    if response.status_code == 200: #is valid
        data = response.json()
        results = data.get("results")

        if results: #has data
            nearest_toll_booth = results[0]
            booth_name = nearest_toll_booth["name"]
            latitude = nearest_toll_booth["geometry"]["location"]["lat"]
            longitude = nearest_toll_booth["geometry"]["location"]["lng"]
            print("located ", booth_name, " at ", latitude, ", ", longitude)
            booth = boothdata(booth_name, latitude, longitude, True)
            return booth
        else:
            print(f"No toll booths were found at {latitude},{longitude} within the specified radius.")
    else:
        print(f"Request failed with status code {response.status_code}")

    return boothdata()



def get_city_coordinates(api_key: str, city_name: str):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        print(f"Error: {data['status']}")
        return coords()

    location = data["results"][0]["geometry"]["location"]
    return coords(location["lat"], location["lng"], True)





#read in data from xlsx and store in a struct

#get api key
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
#find toll booths for each row
    #start by finding beginning
waypoints = []
if (start_city):
waypoints.append(start_city)

find_nearest_toll_booth(api_key, )
    #then end
    #then inbetween