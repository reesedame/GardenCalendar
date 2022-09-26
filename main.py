import requests
import pprint
from datetime import date, timedelta
import apiKeys
import pickle
import pandas as pd
from scipy.spatial.distance import cdist


class Seed:
    def __init__(
        self,
        name,
        lowerIdealTemp,
        upperIdealTemp,
        frostHardy,
        daysToGermination,
        daysToMaturity,
    ):
        self.name = name
        self.lowerIdealTemp = lowerIdealTemp
        self.upperIdealTemp = upperIdealTemp
        self.frostHardy = frostHardy.capitalize()
        self.daysToGermination = daysToGermination
        self.daysToMaturity = daysToMaturity

    def getTotalGrowTime(self):
        return int(self.daysToGermination) + int(self.daysToMaturity)

    def __repr__(self):
        print("\n")
        print("Name: " + self.name)
        print(
            "Ideal Temperature: "
            + self.lowerIdealTemp
            + "-"
            + self.upperIdealTemp
            + "\N{DEGREE SIGN}F"
        )
        if self.frostHardy == "Y":
            print("Frost Hardy: Yes")
        else:
            print("Frost Hardy: No")
        print("Days to Germination: " + self.daysToGermination + " days")
        print("Days to Maturity: " + self.daysToMaturity + " days")


def getNewSeedInfo():
    newSeedInfo = []

    newSeedInfo.append(input("What is the seed?: "))
    newSeedInfo.append(
        input("What is the lower bound of the ideal temperature in fahrenheit?: ")
    )
    newSeedInfo.append(
        input("What is the upper bound of the ideal temperature in fahrenheit?: ")
    )
    newSeedInfo.append(input("Is the seed frost hardy? Y/N: "))
    newSeedInfo.append(input("How many days until germination?: "))
    newSeedInfo.append(input("How many days until maturation?: "))

    return newSeedInfo


def createNewSeed(newSeedInfo):
    newSeed = Seed(
        newSeedInfo[0],
        newSeedInfo[1],
        newSeedInfo[2],
        newSeedInfo[3],
        newSeedInfo[4],
        newSeedInfo[5],
    )

    return newSeed


class User:
    def __init__(self, name, zipCode):
        self.name = name
        self.zipCode = zipCode
        self.seedList = []
        self.latitudeAndLongitude = getLatitudeAndLongitude(zipCode)
        self.weatherStation = getWeatherStation(self.latitudeAndLongitude)
        results = getDailyWeatherSummaries(self.weatherStation, apiKeys.weatherKey)
        self.avgTempMap = getAvgTempMap(results)
        self.avgLowMap = getAvgLowMap(results)
        self.avgHighMap = getAvgHighMap(results)

    def printSeedList(self):
        print("Seed List:")
        listNum = 1
        for seed in self.seedList:
            print(str(listNum) + ". " + seed.name)
            listNum = listNum + 1

    def __repr__(self):
        print("\n")
        print("Name: " + self.name)
        print("Zip code: " + self.zipCode)
        print("Weather Station: " + self.weatherStation)
        print("Seed List:")
        self.printSeedList()


def getNewUserInfo():
    newUserInfo = []

    newUserInfo.append(input("What is your name?: "))

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
        break

    newUserInfo.append(zipCode)

    return newUserInfo


def createNewUser(newUserInfo):
    newUser = User(newUserInfo[0], newUserInfo[1])

    return newUser


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


def pprintMap(map):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(map)


# Returns all dates, as strings, that are within the ideal temperature range for the given seed
def getIdealGrowDates(seed, avgLowMap, avgHighMap, avgTempMap):
    lowTemp = int(seed.lowerIdealTemp)
    highTemp = int(seed.upperIdealTemp)

    # Could use sets instead of lists
    # & then idealGrowDateStrs would be a union of the two sets

    idealGrowDates = []

    # If the seed is frost hardy...
    if seed.frostHardy == "Y":
        avgLowDates = list(avgLowMap.keys())
        avgHighDates = list(avgHighMap.keys())

        # Remove dates that have an avg low below 32
        avgLowDates = list(filter(lambda date: (avgLowMap[date] > 32), avgLowDates))

        # Remove dates that have an avg high > highTemp
        avgHighDates = list(
            filter(lambda date: (avgHighMap[date] < highTemp), avgHighDates)
        )

        # Add dates still remain in both avgLowDates & avgHighDates to idealGrowDateStrs
        for date in avgLowDates:
            if date in avgHighDates:
                idealGrowDates.append(convertToDate(date))

    # If the seed is not frost hardy...
    else:
        # Add dates that have an avg temp >= lowTemp and <= highTemp to idealGrowDateStrs
        for date in avgTempMap:
            if avgTempMap[date] >= lowTemp and avgTempMap[date] <= highTemp:
                idealGrowDates.append(convertToDate(date))

    return idealGrowDates


# Helper method - converts date string to Date object
def convertToDate(strDate):
    # Year is an arbitrary value that will not be shown to the user
    # 2020 is used as it was the last leap year
    year = 2020
    month = int(strDate[:2])
    day = int(strDate[len(strDate) - 2 :])

    return date(year, month, day)


# Returns a list of date ranges, represented by tuples
def getSowDateRanges(seed, idealGrowDates):
    totalGrowTime = seed.getTotalGrowTime()

    sowDateRanges = []

    dateRangeStartIdx = 0
    dateRangeEndIdx = 0

    for i in range(len(idealGrowDates) - 1):
        # Calculate difference in dates from index to index
        dateDifference = int((idealGrowDates[i + 1] - idealGrowDates[i]).days)
        # If the difference is greater than one, there is a gap of dates where temp is not ideal
        # & these dates will not be included in the sowDateRange
        if dateDifference > 1:
            # Year is set to 2020 to ensure that it is within idealGrowDates
            lastSowDate = (idealGrowDates[i] - timedelta(days=totalGrowTime)).replace(
                year=2020
            )
            dateRangeEndIdx = idealGrowDates.index(lastSowDate)

            sowDateRanges.append(
                (
                    idealGrowDates[dateRangeStartIdx],
                    idealGrowDates[dateRangeEndIdx],
                )
            )

            dateRangeStartIdx = i + 1

        # Add last range of dates
        if i == len(idealGrowDates) - 2:
            # If growing temps are not ideal in January, the final date in idealGrowDates
            # will be considered the final harvest date, which allows us to calculate
            # an ideal lastSowDate
            if idealGrowDates[0] != date(2020, 1, 1):
                lastSowDate = idealGrowDates[i] - timedelta(days=totalGrowTime)
                dateRangeEndIdx = idealGrowDates.index(lastSowDate)

                sowDateRanges.append(
                    (
                        idealGrowDates[dateRangeStartIdx],
                        idealGrowDates[dateRangeEndIdx],
                    )
                )
            # If growing temps are ideal in January, then the lastSowDate can be the final date
            # in convertedGrowDates
            else:
                sowDateRanges.append(
                    (
                        idealGrowDates[dateRangeStartIdx],
                        idealGrowDates[i + 1],
                    )
                )

    return sowDateRanges


def printSowDateRanges(sowDateRanges):
    for dateRange in sowDateRanges:
        print(dateRange[0].strftime("%B %-d") + " - " + dateRange[1].strftime("%B %-d"))


# Calculates an estimated harvest date based on the seed's total grow time
def getHarvestDate(seed, strSowDate):
    year = int(strSowDate[6:])
    month = int(strSowDate[:2])
    day = int(strSowDate[3:5])
    sowDate = date(year, month, day)
    return sowDate + timedelta(days=seed.getTotalGrowTime())


def displayMenu():
    print("\n" + "* * * * * * * * * *" + "\n")
    print("1. Get sow dates for saved seeds")
    print("2. Enter new seed")
    print("3. Quit")
    print("\n" + "* * * * * * * * * *" + "\n")


def main():
    try:
        user = pickle.load(open("pickledUser.pkl", "rb"))
        print(f"Hello {user.name} and welcome back to the Garden Calendar!")
        print(
            "As you probably remember, this program helps you determine the best date to sow your seeds outdoors."
        )
    except:
        print("Hello and welcome to the Garden Calendar!")
        print(
            "You can use this program to help you determine the best date to sow your seeds outdoors."
        )
        print(
            "It looks like you're new here. I will need to collect some info before we get started."
        )
        userInfo = getNewUserInfo()
        user = createNewUser(userInfo)

    while True:
        displayMenu()

        userChoice = input("Menu option: ")
        userChoice = userChoice.strip()
        print("\n" + "* * * * * * * * * *" + "\n")

        if userChoice == "1":
            if len(user.seedList) < 1:
                print(
                    "You have not entered any seeds. You must enter a seed before you can get a sow date."
                )
            else:
                user.printSeedList()
                print("\n" + "* * * * * * * * * *" + "\n")

                while True:
                    selectedSeedNum = input("Enter seed: ")

                    try:
                        selectedSeedNum = int(selectedSeedNum.strip())
                        selectedSeedIdx = selectedSeedNum - 1
                        if selectedSeedIdx < len(user.seedList):
                            selectedSeed = user.seedList[selectedSeedIdx]
                        else:
                            print(
                                "Invalid option. Please enter a number from the list of saved seeds."
                            )
                            continue
                    except:
                        print(
                            "Invalid option. Please enter a number from the list of saved seeds."
                        )
                        continue

                    break

                print("\n" + "* * * * * * * * * *" + "\n")

                idealGrowDates = getIdealGrowDates(
                    selectedSeed, user.avgLowMap, user.avgHighMap, user.avgTempMap
                )

                sowDateRanges = getSowDateRanges(selectedSeed, idealGrowDates)

                if len(sowDateRanges) > 0:
                    print(f"Best sow dates for {selectedSeed.name}:\n")
                    printSowDateRanges(sowDateRanges)
                    print("\n" + "* * * * * * * * * *" + "\n")

                    while True:
                        try:
                            print("What day do you plan to sow your seeds?")
                            plannedSowDate = input(
                                "Please enter a date within the ranges above (format MM-DD-YYYY): "
                            )
                            print("\n" + "* * * * * * * * * *" + "\n")

                            estHarvestDate = getHarvestDate(
                                selectedSeed, plannedSowDate
                            )
                            print(
                                "If you sow your seeds on "
                                + plannedSowDate
                                + "... \nthe estimated harvest date is "
                                + estHarvestDate.strftime("%m-%d-%Y")
                            )
                        except:
                            print(
                                "Invalid entry. Please enter a date in the format MM-DD-YYYY\n"
                            )
                            continue
                        break

                else:
                    print("I am sorry. I could not find any good sow dates.")
                    print("Perhaps you should start these seeds indoors.")
                    print("\n" + "* * * * * * * * * *" + "\n")

        elif userChoice == "2":
            newSeedInfo = getNewSeedInfo()
            user.seedList.append(createNewSeed(newSeedInfo))
            pickle.dump(user, open("pickledUser.pkl", "wb"))
            print("The new seed has been added to your seed list.")

        elif userChoice == "3":
            print(
                "Thank you for using the Garden Calendar! I hope you have an abundant harvest!"
            )
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please enter a number from the provided menu.")


main()
