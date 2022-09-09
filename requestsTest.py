import requests
import pprint

# # See docs: https://docs.python.org/3/library/pprint.html
# pp = pprint.PrettyPrinter(indent=4)

# NOAAToken = "FleUDTUZVCskzNVEDjXAVlRnwScChsfk"

# headers = {"token:" + NOAAToken}
# params = {}
# endpoint = "https://www.ncei.noaa.gov/cdo-web/api/v2/datasets"

# response = requests.get(endpoint, headers=headers, params=params)

# # dir(response) gets you all available methods to response

# res_json = response.json()

# # res_json.keys() get's you all of the keys of the res_json dictionary

# metadata = res_json["metadata"]
# results = res_json["results"]

# # dict comprehension
# id_desc_map = {r["id"]: r["name"] for r in results}

# # The above is equivalent to the following loop
# # id_desc_map = {}
# # for r in results:
# #   id_desc_map[r['id']] = r['name']

# pp.pprint(id_desc_map)

# Visual crossing weather API
userZip = input("What is your zipcode?: ")
visualCrossingKey = "26ZYQLE9KRYC4LLDLE7PKR3DP"
requestURL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{zipCode}?unitGroup=us&elements=datetime%2Cname%2Clatitude%2Clongitude%2Cstations&include=days%2Cobs&key={key}&maxStations=1&contentType=json".format(
    zipCode=userZip, key=visualCrossingKey
)
response = requests.get(requestURL)
res_json = response.json()
stations = res_json["stations"]


def getWeatherStation(stations):
    for station in stations:
        if station[0] == "K":
            return station


weatherStation = getWeatherStation(stations)
print(weatherStation)
