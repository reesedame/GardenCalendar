# Garden Calendar

I created the Garden Calendar to help user's determine appropriate dates to sow their seeds outdoors based on seed information and the user's local weather history.

Once the program starts, the user is prompted to enter their name and zip code. The zip code's correlating latitude and longitude are then found by reading zipcodes.csv via pandas. The latitude and longitude are then used to determine the closest weather station. Finally, the closest weather station ID is used in IBM's Weather Data API to collect historical data - average temperature, average high temperature, and average low temperature for each day of the year. Based on the ideal temperature range for the seed, a range of ideal grow dates will be provided to the user. The user can then get an estimated harvest date by providing their planned sow date.

I have not included my API key, so you will have to obtain one in order to run the program. A key for IBM's Weather Data API can be obtained by inspecting the network calls from Accuweather.

To run the main program, all you have to do is run the main.py file. I hope you enjoy!

### Upcoming Features:

- Recommend if and when a seed should be started indoors instead
- ~~Determine an alternative way to determine the user's closest weather station to reduce the network impact~~
- Utilize a web scraper to obtain seed's information
- ~~Save & reload user data - like the user's closest weather station and seeds they have entered~~
