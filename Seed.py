class Seed:
    def __init__(self):
        self.name = input("What is the seed?: ")
        self.lowerIdealTemp = input(
            "What is the lower bound of the ideal temperature in fahrenheit?: "
        )
        self.upperIdealTemp = input(
            "What is the upper bound of the ideal temperature in fahrenheit?: "
        )
        self.frostHardy = (input("Is the seed frost hardy? Y/N: ")).capitalize()
        self.daysToGermination = input("How many days until germination?: ")
        self.daysToMaturity = input("How many days until maturation?: ")

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
