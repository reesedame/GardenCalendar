import requests
import pprint
from datetime import date, timedelta
import apiKeys


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

    def printAttributes(self):
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
        self.zipCode = int(zipCode)
        self.weatherStation = getWeatherStation(zipCode, apiKeys.visualCrossingKey)

    def printAttributes(self):
        print("\n")
        print("Name: " + self.name)
        print("Zip code: " + self.zipCode)
        print("Weather Station: " + self.weatherStation)


def getNewUserInfo():
    newUserInfo = []

    newUserInfo.append(input("What is your name?: "))
    newUserInfo.append(input("What is your zip code?: "))

    return newUserInfo


def createNewUser(newUserInfo):
    newUser = User(newUserInfo[0], int(newUserInfo[1]))

    return newUser


def getWeatherStation(userZip, apiKey):
    requestURL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{zipCode}?unitGroup=us&elements=datetime%2Cname%2Clatitude%2Clongitude%2Cstations&include=days%2Cobs&key={key}&maxStations=1&contentType=json".format(
        zipCode=userZip, key=apiKey
    )
    response = requests.get(requestURL)
    res_json = response.json()
    stations = res_json["stations"]

    for station in stations:
        if station[0] == "K":
            return station


def getDailyWeatherSummaries(weatherStation, apiKey):
    requestURL = "https://api.weather.com/v1/location/{weatherStation}:9:US/almanac/daily.json?apiKey={apiKey}&units=e&start=0101&end=1231".format(
        weatherStation=weatherStation, apiKey=apiKey
    )
    response = requests.get(requestURL)

    return response.json()


def getDailyWeatherSummariesMetadata(res_json):
    return res_json["metadata"]


def getDailyWeatherSummariesResults(res_json):
    return res_json["almanac_summaries"]


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
def getIdealGrowDateStrs(seed, avgLowMap, avgHighMap, avgTempMap):
    lowTemp = int(seed.lowerIdealTemp)
    highTemp = int(seed.upperIdealTemp)
    avgLowDates = list(avgLowMap.keys())
    avgHighDates = list(avgHighMap.keys())

    idealGrowDateStrs = []

    # If the seed is frost hardy...
    if seed.frostHardy == "Y":
        # Remove dates that have an avg low below 32
        for date in avgLowMap:
            if avgLowMap[date] < 32:
                avgLowDates.remove(date)
        # Remove dates that have an avg high > highTemp
        for date in avgHighMap:
            if avgHighMap[date] > highTemp:
                avgHighDates.remove(date)
        # Add dates still remain in both avgLowDates & avgHighDates to idealGrowDateStrs
        for date in avgLowDates:
            if date in avgHighDates:
                idealGrowDateStrs.append(date)
    # If the seed is not frost hardy...
    else:
        # Add dates that have an avg temp >= lowTemp and <= highTemp to idealGrowDateStrs
        for date in avgTempMap:
            if avgTempMap[date] >= lowTemp and avgTempMap[date] <= highTemp:
                idealGrowDateStrs.append(date)

    return idealGrowDateStrs


# Converts date string to Date object
def convertToDate(strDate):
    # Year is an arbitrary value that will not be shown to the user
    # 2020 is used as it was the last leap year
    year = 2020
    month = int(strDate[:2])
    day = int(strDate[len(strDate) - 2 :])

    return date(year, month, day)


# Converts return from getIdealGrowDateStrs() from a list of strings to a list of Date objects
def getConvertedGrowDates(idealGrowDateStrs):
    convertedGrowDates = []

    for date in idealGrowDateStrs:
        convertedGrowDates.append(convertToDate(date))

    return convertedGrowDates


# Returns date ranges as a list of dates
# For example: index 0 is the start of the range and index 1 is the end
def getSowDateRanges(seed, convertedGrowDates):
    totalGrowTime = seed.getTotalGrowTime()

    sowDateRanges = []

    dateRangeStartIdx = 0
    dateRangeEndIdx = 0

    for i in range(len(convertedGrowDates) - 1):
        # Calculate difference in dates from index to index
        dateDifference = int((convertedGrowDates[i + 1] - convertedGrowDates[i]).days)
        # If the difference is greater than one, there is a gap of dates where temp is not ideal
        # & these dates will not be included in the sowDateRange
        if dateDifference > 1:
            lastSowDate = convertedGrowDates[i] - timedelta(days=totalGrowTime)
            dateRangeEndIdx = convertedGrowDates.index(lastSowDate)

            sowDateRanges.append(convertedGrowDates[dateRangeStartIdx])
            sowDateRanges.append(convertedGrowDates[dateRangeEndIdx])

            dateRangeStartIdx = i + 1

        # Add last range of dates
        if i == len(convertedGrowDates) - 2:
            # If growing temps are not ideal in January, the final date in convertedGrowDates
            # will be considered the final harvest date, which allows us to calculate
            # an ideal lastSowDate
            if convertedGrowDates[0] != date(2020, 1, 1):
                lastSowDate = convertedGrowDates[i] - timedelta(days=totalGrowTime)
                dateRangeEndIdx = convertedGrowDates.index(lastSowDate)

                sowDateRanges.append(convertedGrowDates[dateRangeStartIdx])
                sowDateRanges.append(convertedGrowDates[dateRangeEndIdx])
            # If growing temps are ideal in January, then the lastSowDate can be the final date
            # in convertedGrowDates
            else:
                sowDateRanges.append(convertedGrowDates[dateRangeStartIdx])
                sowDateRanges.append(convertedGrowDates[i + 1])

    return sowDateRanges


def printSowDateRanges(sowDateRanges):
    for i in range(len(sowDateRanges)):
        if i % 2 != 0:
            dateRangeStart = sowDateRanges[i - 1].strftime("%B %-d")
            dateRangeEnd = sowDateRanges[i].strftime("%B %-d")
            print(dateRangeStart + " - " + dateRangeEnd)


# Calculates an estimated harvest date based on the seed's total grow time
def getHarvestDate(seed, strSowDate):
    year = int(strSowDate[6:])
    month = int(strSowDate[:2])
    day = int(strSowDate[3:5])
    sowDate = date(year, month, day)
    return sowDate + timedelta(days=seed.getTotalGrowTime())


# Main Program
def main():
    print("\n" + "* * * * * * * * * *" + "\n")
    print("Hello and welcome to the Garden Calendar!")
    print(
        "You can use this program to help you determine the best date to sow your seeds outdoors."
    )
    print("\n" + "* * * * * * * * * *" + "\n")

    print("In order to do this, I will need some information from you...")
    newUserInfo = getNewUserInfo()
    user = createNewUser(newUserInfo)
    print("\n" + "* * * * * * * * * *" + "\n")

    print(
        "Thank you, {userName}. Now I will need information about the seed you want to sow. \n".format(
            userName=user.name
        )
    )
    newSeedInfo = getNewSeedInfo()
    seed = createNewSeed(newSeedInfo)
    print("\n" + "* * * * * * * * * *" + "\n")

    response_json = getDailyWeatherSummaries(user.weatherStation, apiKeys.weatherKey)
    results = getDailyWeatherSummariesResults(response_json)
    avgTempMap = getAvgTempMap(results)
    avgLowMap = getAvgLowMap(results)
    avgHighMap = getAvgHighMap(results)

    idealGrowDateStrs = getIdealGrowDateStrs(seed, avgLowMap, avgHighMap, avgTempMap)
    convertedGrowDates = getConvertedGrowDates(idealGrowDateStrs)
    sowDateRanges = getSowDateRanges(seed, convertedGrowDates)

    if len(sowDateRanges) > 0:
        print(
            "Here are the ranges of dates when it would be best to sow {seedName}:".format(
                seedName=seed.name
            )
        )
        print("\n")
        printSowDateRanges(sowDateRanges)
        print("\n" + "* * * * * * * * * *" + "\n")
    else:
        print("I am sorry. I could not find any good sow dates.")
        print("Perhaps you should start these seeds indoors.")
        exit()

    print("I can also give you an estimated harvest date. \n")
    print("What day do you plan to sow your seeds?")
    plannedSowDate = input(
        "Please enter a date within the ranges above in the format MM-DD-YYYY: "
    )
    print("\n")
    estHarvestDate = getHarvestDate(seed, plannedSowDate)
    print(
        "If you sow your seeds on "
        + plannedSowDate
        + "... \nthe estimated harvest date is "
        + estHarvestDate.strftime("%m-%d-%Y")
    )
    print("\n" + "* * * * * * * * * *" + "\n")


main()
