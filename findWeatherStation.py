import pandas as pd
from scipy.spatial.distance import cdist


def getLatitudeAndLongitude(zipcode):
    zipcodes = pd.read_csv("zipcodes.csv")
    records = zipcodes.loc[(zipcodes["Zipcode"] == zipcode)]
    return (records["Lat"].mean(), records["Long"].mean())


def getWeatherStation(latAndLong):
    stations = pd.read_csv("weatherStations.csv")
    locations = [(x, y) for x, y in zip(stations["Latitude"], stations["Longitude"])]
    closest = locations[cdist([latAndLong], locations).argmin()]
    stationID = stations.loc[
        (stations["Latitude"] == closest[0]) & (stations["Longitude"] == closest[1])
    ]["STID"].values[0]
    return stationID


def main():
    zipcode = input("What is your zipcode?: ")
    latAndLong = getLatitudeAndLongitude(int(zipcode))
    weatherStation = getWeatherStation(latAndLong)
    print(weatherStation)
    print(type(weatherStation))


main()
