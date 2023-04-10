# Thomas Dixon
# teddixon@umich.edu
# 04 / 10 / 2023

import os
import requests
from dotenv import load_dotenv
from haversine import haversine
import webbrowser
import math
import openpyxl
from typing import List
import csv

load_dotenv()

class boothdata:
    def __init__(self, name = "Null", lat = -1.0, lon = -1.0, valid = False):
        self.name = name
        self.lon = lat
        self.lat = lon
        self.valid = valid

class coords:
    def __init__(self, lat = -1.0, lon = -1.0, valid = False):
        self.lat = lat
        self.lon = lon
        self.valid = valid
        
def write_file(file_path, data):
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(data)


def find_nearest_toll_booth(api_key: str, latitude: float, longitude: float, radius: int = 10000) -> boothdata:
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
            #get data
            nearest_toll_booth = results[0]
            booth_name = nearest_toll_booth["name"]
            latitude = nearest_toll_booth["geometry"]["location"]["lat"]
            longitude = nearest_toll_booth["geometry"]["location"]["lng"]
            #print data and return
            print("located ", booth_name, "at", latitude, ",", longitude)
            return boothdata(booth_name, latitude, longitude, True)
        else:
            print(f"No toll booths were found at {latitude},{longitude} within the specified radius.")
    else:
        print(f"Request failed with status code {response.status_code}")

    return boothdata()


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


def get_toll_booth_on_route(api_key: str, slatitude: float, slongitude: float, elatitude: float, elongitude: float, booths: List[boothdata], radius: int = 1000) -> List[boothdata]:
    #build directions URL and get response
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={slatitude},{slongitude}&destination={elatitude},{elongitude}&key={api_key}"
    directions_response = requests.get(directions_url)
    directions_data = directions_response.json()

    #if directions response data contains an error, return None
    if directions_data["status"] != "OK":
        print(f"Error: {directions_data['status']}")
        return None

    # Extract the route's polyline and decode into points
    polyline = directions_data["routes"][0]["overview_polyline"]["points"]

    # Decode the polyline into a list of coordinates
    coordinates = decode_polyline(polyline)

    # Sample the coordinates at decreasing intervals
    found = len(booths)
    samp = 200

    while found < 2:
        samp = int(math.ceil(samp/2))
        sampled_coordinates = coordinates[::int(math.ceil(samp))]
        
        for coord in sampled_coordinates:
            booth = find_nearest_toll_booth(api_key, coord[0], coord[1], radius)
            
            if booth in booths:
                continue
            
            booths.append(booth)
            found+=1
    return booths
                
            



def get_city_coordinates(api_key: str, city_name: str):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        print(f"Error: {data['status']}")
        return coords()

    location = data["results"][0]["geometry"]["location"]
    return coords(location["lat"], location["lng"], True)


def read_xlsx_file(file_path):
    # Load the workbook and select the first sheet
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    data = []

    # Iterate through the rows and columns, extracting the first 13 columns
    flag = True
    for row in ws.iter_rows():
        if flag == True: #skip header
            flag = False
            continue
        row_data = []
        for cell in row[:13]:
            # Get the cell value and convert it to a string
            cell_value = str(cell.value) if cell.value is not None else ""
            row_data.append(cell_value)
        data.append(row_data)

    return data




#read in data from xlsx and store in a struct
input_file_path = "input.xlsx"
data = read_xlsx_file(input_file_path)
output_file_path = "output.tsv"
with open(output_file_path, 'w') as file:
    pass

#get api key
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

#find toll booths for each row
for row in data:
    print(row)
    waypoints = []
    if (row[2] != "" and row[2] != "Na" and row[2] != "na" and row[2] != "0"): #get start
        cds = get_city_coordinates(api_key, row[2])
        if (cds.valid != False):
            waypoints.append(cds)
            
    if (row[3] != "" and row[3] != "Na" and row[3] != "na" and row[3] != "0"): #get dest
        cds = get_city_coordinates(api_key, row[3])
        if (cds.valid != False):
            waypoints.append(cds)
        
    if (row[4] != "" and row[4] != "Na" and row[4] != "na" and row[4] != "0"): #get city1
        cds = get_city_coordinates(api_key, row[4])
        if (cds.valid != False):
            waypoints.append(cds)
        
    if (row[5] != "" and row[5] != "Na" and row[5] != "na" and row[5] != "0"): #get city2
        cds = get_city_coordinates(api_key, row[5])
        if (cds.valid != False):
            waypoints.append(cds)
        
    if (row[6] != "" and row[6] != "Na" and row[6] != "na" and row[6] != "0"): #get city3
        cds = get_city_coordinates(api_key, row[6])
        if (cds.valid != False):
            waypoints.append(cds)
        
    if (row[7] != "" and row[7] != "Na" and row[7] != "na" and row[7] != "0"): #get city4
        cds = get_city_coordinates(api_key, row[7])
        if (cds.valid != False):
            waypoints.append(cds)   
    
    
    #find toll booths at waypoints
    toll_booths = []
    for city_cds in waypoints:
        toll_booth = find_nearest_toll_booth(api_key, city_cds.lat, city_cds.lon)
        if toll_booth.valid != False:
            toll_booths.append(toll_booth)
    
    
    
    unique_booth_data = {}
    for booth in toll_booths:
        # Add the booth to the dictionary if it's not already there
        if booth.name not in unique_booth_data:
            unique_booth_data[booth.name] = booth

    # Convert the dictionary values back to a list
    unique_booth_data_array = list(unique_booth_data.values())
    
    if len(unique_booth_data_array) < 2:
        if len(waypoints) > 1:
            unique_booth_data_array = get_toll_booth_on_route(api_key, waypoints[0].lat, waypoints[0].lon, waypoints[1].lat, waypoints[1].lon, unique_booth_data_array)
            
    
    #print all toll booths
    for toll_booth in toll_booths:
        print("Toll booth: ", toll_booth.name, " ", toll_booth.lat, " ", toll_booth.lon, " ", toll_booth.valid, "\n",)
        
    l = list()
    l.append(row[0])
    l.append(row[2])
    l.append(row[3])
        
    if len(toll_booths) == 0:
        l.append("NODATA")
        write_file(output_file_path, l)
    elif len(toll_booths) == 1:
        l.append(f"{toll_booths[0].name}, {toll_booths[0].lat}, {toll_booths[0].lon}")
        write_file(output_file_path, l)
    elif len(toll_booths) == 2:
        l.append(f"{toll_booths[0].name}, {toll_booths[0].lat}, {toll_booths[0].lon}")
        l.append(f"{toll_booths[1].name}, {toll_booths[1].lat}, {toll_booths[1].lon}")
        write_file(output_file_path, l)
    elif len(toll_booths) == 3:
        l.append(f"{toll_booths[0].name}, {toll_booths[0].lat}, {toll_booths[0].lon}")
        l.append(f"{toll_booths[1].name}, {toll_booths[1].lat}, {toll_booths[1].lon}")
        l.append(f"{toll_booths[2].name}, {toll_booths[2].lat}, {toll_booths[2].lon}")
        write_file(output_file_path, l)
    else:
        l.append(f"{toll_booths[0].name}, {toll_booths[0].lat}, {toll_booths[0].lon}")
        l.append(f"{toll_booths[1].name}, {toll_booths[1].lat}, {toll_booths[1].lon}")
        l.append(f"{toll_booths[2].name}, {toll_booths[2].lat}, {toll_booths[2].lon}")
        l.append(f"{toll_booths[3].name}, {toll_booths[3].lat}, {toll_booths[3].lon}")
        write_file(output_file_path, l)