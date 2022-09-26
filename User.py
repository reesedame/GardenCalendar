from Seed import Seed
import apiKeys
import requests
import pandas as pd
from scipy.spatial.distance import cdist


class User:
    def __init__(self):
        self.name = input("What is your name?: ")

        while True:
            zipCode = input("What is your zip code?: ")

            try:
                if len(zipCode.strip()) == 5:
                    zipCode = int(zipCode)
                else:
                    print("Zip code must be 5 digits. Please try again.")
                    continue
            except:
                print("Zip code must be 5 digits. Please try again.")
                continue

            self.zipCode = zipCode
            break

        self.seedList = []
        self.latitudeAndLongitude = getLatitudeAndLongitude(zipCode)
        self.weatherStation = getWeatherStation(self.latitudeAndLongitude)
        results = getDailyWeatherSummaries(self.weatherStation, apiKeys.weatherKey)
        self.avgTempMap = getAvgTempMap(results)
        self.avgLowMap = getAvgLowMap(results)
        self.avgHighMap = getAvgHighMap(results)

    def printSeedList(self):
        print("Seed List:")
        for num, seed in enumerate(self.seedList, start=1):
            print(str(num) + ". " + seed.name)

    def __repr__(self):
        print("\n")
        print("Name: " + self.name)
        print("Zip code: " + self.zipCode)
        print("Weather Station: " + self.weatherStation)
        print("Seed List:")
        self.printSeedList()


def getLatitudeAndLongitude(zipCode):
    zipCodes = pd.read_csv("zipcodes.csv", usecols=["Zipcode", "Lat", "Long"])
    records = zipCodes.loc[(zipCodes["Zipcode"] == zipCode)]
    return (records["Lat"].mean(), records["Long"].mean())


def getWeatherStation(latAndLong):
    stations = pd.read_csv("weatherStations.csv")
    locations = [(x, y) for x, y in zip(stations["Latitude"], stations["Longitude"])]
    closest = locations[cdist([latAndLong], locations).argmin()]
    stationID = stations.loc[
        (stations["Latitude"] == closest[0]) & (stations["Longitude"] == closest[1])
    ]["STID"].values[0]
    return stationID


def getDailyWeatherSummaries(weatherStation, apiKey):
    requestURL = "https://api.weather.com/v1/location/{weatherStation}:9:US/almanac/daily.json?apiKey={apiKey}&units=e&start=0101&end=1231".format(
        weatherStation=weatherStation, apiKey=apiKey
    )
    response = requests.get(requestURL)

    return response.json()["almanac_summaries"]


def getAvgLowMap(results):
    return {r["almanac_dt"]: r["avg_lo"] for r in results}


def getAvgHighMap(results):
    return {r["almanac_dt"]: r["avg_hi"] for r in results}


def getAvgTempMap(results):
    return {r["almanac_dt"]: r["mean_temp"] for r in results}
