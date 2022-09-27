import requests
from bs4 import BeautifulSoup


class Seed:
    def __init__(self, seedInfo):
        self.name = seedInfo[0]
        self.lowerIdealTemp = seedInfo[1]
        self.upperIdealTemp = seedInfo[2]
        self.frostHardy = seedInfo[3].capitalize()
        self.daysToGermination = seedInfo[4]
        self.daysToMaturity = seedInfo[5]

    def getSeedInfoFromUser():
        seedInfo = []

        seedInfo.append(input("What is the seed?: "))
        seedInfo.append(
            input("What is the lower bound of the ideal temperature in fahrenheit?: ")
        )
        seedInfo.append(
            input("What is the upper bound of the ideal temperature in fahrenheit?: ")
        )
        seedInfo.append(input("Is the seed frost hardy? Y/N: "))
        seedInfo.append(input("How many days until germination?: "))
        seedInfo.append(input("How many days until maturation?: "))

        return seedInfo

    # Returns daysToMaturity for a searched seed.
    # If value cannot be found, then user is asked for input.
    def getDaysToMaturity(seedOverview):
        paragraph = seedOverview.find("span").contents[0]

        if paragraph[0].isdigit():
            words = paragraph.split()
            if "-" in words[0]:
                daysToMaturityRange = words[0].split("-")
                return (int(daysToMaturityRange[0]) + int(daysToMaturityRange[1])) // 2
            else:
                return words[0]
        else:
            print("Unable to find days until maturation.")

        while True:
            daysToMaturity = input(
                "Please enter days to maturity for the selected seed: "
            )

            try:
                daysToMaturity = int(daysToMaturity.strip())
            except:
                print("Invalid entry. Please enter a number.")
                continue
            break

        return daysToMaturity

    # Returns list item from seedData that contains the provided string s
    def getFilteredListItem(s, seedData):
        return list(filter(lambda listItem: (s in listItem), seedData))[0]

    def getIdealTempRange(seedData):
        # Get list item that contains "Ideal" from seedData & split into a list of strings
        idealTempStringWordList = Seed.getFilteredListItem("Ideal", seedData).split()

        # Get string that contains digits
        tempRange = list(
            filter(
                lambda word: (any(char.isdigit() for char in word)),
                idealTempStringWordList,
            )
        )

        # return idealTempRange as a list
        # [0] is the lower temp & [1] is the higher temp
        return tempRange[0].split("-")

    def getFrostHardy(seedData):
        # Get list item that contains "Frost" from seedData & split into a list of strings
        frostHardyStringWordList = Seed.getFilteredListItem("Frost", seedData).split()

        # Yes/No value of frostHardy is always at index 2
        frostHardy = frostHardyStringWordList[2]

        # Return capitalized first character of frostHardy
        return frostHardy[0].capitalize()

    def getDaysToGermination(seedData):
        # Get list item that contains "Sprouts" from seedData & split into a list of strings
        germinationStringWordList = Seed.getFilteredListItem(
            "Sprouts", seedData
        ).split()

        # Get string that contains digits
        daysRange = list(
            filter(
                lambda word: (any(char.isdigit() for char in word)),
                germinationStringWordList,
            )
        )

        # Split string into a list of digits
        daysRangeList = daysRange[0].split("-")

        # Return average of digits
        return (int(daysRangeList[0]) + int(daysRangeList[1])) // 2

    def searchForSeedInfo():
        while True:
            seedToSearch = input("What seed would you like to search for?: ")

            try:
                url = (
                    f"https://www.rareseeds.com/catalogsearch/result/?q={seedToSearch}"
                )
                searchData = requests.get(url).text
                searchDataSoup = BeautifulSoup(searchData, "lxml")
                foundSeeds = searchDataSoup.find_all("span", {"class": "product--name"})
                seedNames = [seed.text.split("\n\n")[1] for seed in foundSeeds]

                for num, name in enumerate(seedNames, start=1):
                    print(str(num) + ". " + name)

            except:
                if not foundSeeds:
                    print(
                        "No seeds found! Try a different search term or search for a different seed."
                    )
                    continue
            break

        # Select seed
        while True:
            selectedSeedInput = input("Please select a seed from the list: ")

            try:
                selectedSeedIdx = int(selectedSeedInput.strip()) - 1
                if selectedSeedIdx < len(seedNames):
                    selectedSeed = foundSeeds[selectedSeedIdx]
                else:
                    print(
                        "Invalid option. Please enter a number from the list of found seeds."
                    )
                    continue
            except:
                print(
                    "Invalid option. Please enter a number from the list of found seeds."
                )
                continue
            break

        selectedSeedURL = selectedSeed.find("a")["href"]
        seedDataRequest = requests.get(selectedSeedURL).text
        seedSoup = BeautifulSoup(seedDataRequest, "lxml")
        seedOverview = seedSoup.find("div", {"class": "product attribute overview"})
        seedDataList = seedOverview.find_all("li")
        seedData = [data.get_text() for data in seedDataList]

        daysToMaturity = Seed.getDaysToMaturity(seedOverview)
        idealTempRange = Seed.getIdealTempRange(seedData)
        frostHardy = Seed.getFrostHardy(seedData)
        daysToGermination = Seed.getDaysToGermination(seedData)

        return [
            seedNames[selectedSeedIdx],
            idealTempRange[0],
            idealTempRange[1],
            frostHardy,
            daysToGermination,
            daysToMaturity,
        ]

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
