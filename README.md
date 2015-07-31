This is a personalized recommendation system for traveling.

The application helps residents of the San Francisco Bay Area pick a US city for a weekend trip (from Friday evening to Sunday evening). The user provides as input:

* an upper limit for the airfare (e.g. $500)

as well as the importance, on a scale from 0 to 10, of several factors including:

* weather
* restaurants and bars
* safety
* city size (population)

The output of the application is the top 10 US cities according to the user's input.

Here is a sample input for the application:

|Parameter    | Value (selected by the user) |
|-------------|------------------------------|
|airfare      |          $700                |
|weather      |          4/10                |
|bars         |          7/10                |
|safety       |          9/10                |
|city size    |          1/10                |

and the corresponding output file for this input:

https://github.com/cedar10b/travelapp/blob/master/fig.png

|Best match       | San Diego, CA |
|-----------------|---------------|
|Cost of airfare: | 496.2         |
|Temperature from | 68 to  75  F  |
|Weather forecast | Partly Cloudy |





