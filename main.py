import pandas as pd
import requests
import matplotlib.pyplot as plt
import dateutil.parser


def get_values(site_code=3179000):
    #2 empty lists that will have the needed values in it
    values = []
    dates = []

    url = 'https://waterservices.usgs.gov/nwis/dv/?format=json&sites=0{}&period=P7D&siteType=ST&siteStatus=all'.format(site_code)
    print("Concatinated URL = {}".format(url))
    
    #to check if the site code is actaully a site code
    url_check = requests.get(url)
    print("HTTP Error code = {}".format(url_check))
    #if satement for variable above ^^^
    if url_check.status_code != 200:
        print("[*] ERROR URL IS BAD")
    
    #a pandas function to open a json
    data = pd.read_json(url)
    #converting the json into a dataframe fro easy data manipulation
    dataframe = pd.DataFrame(data)
    
    #looping thorugh the dataframe/JSON to get the value and date for the given site and days
    for index in dataframe['value']['timeSeries'][0]['values'][0]['value']:
        #singular value that is in the data retrived by an index key
        raw_value = index['value']
        raw_date = index['dateTime']
        #slicing the long date and time to just get the day in DD format
        prevelant_date = raw_date[8:-13]
        #appending values to the empty lists
        values.append(float(raw_value))
        dates.append(float(prevelant_date))
    return values, dates

#getting the return values into independant variables
x_values, y_values = get_values(3179000)

#making a new matplotlib graph
plt.figure("Hydrograph for site 0{} and parameter 00060")
plt.style.use('seaborn-notebook')

#characteristics of the graph
plt.ylabel("Discharge, cubic feet per second")
plt.xlabel("past 7 days of water discharge.")

#plotting the data to the graph
plt.plot(y_values, x_values, label="discharge")
plt.legend()
plt.show()

#debugging statement to see the if the JSON values correspond
print("X Values = {}\nY Values = {}".format(x_values, y_values))

