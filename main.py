import pandas as pd
import requests
import matplotlib.pyplot as plt
import dateutil.parser


def get_value(site_code=3179000):
    #2 empty lists that will have the needed values in it
    values = []
    dates = []

    url = 'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=0{}&period=P1D&siteType=ST&siteStatus=all'.format(site_code)
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
        values.append(raw_value)
        dates.append(prevelant_date)
    return values, dates


def plot_graph(x_values, y_values, site_code=3179000):
    plt.figure("Hydrograph for site 0{} and parameter 00060".format(site_code))
    plt.style.use('seaborn-notebook')

    plt.ylabel("Discharge, cubic feet per second")
    plt.xlabel("past 7 days of water discharge.")
    plt.plot(x_values, y_values, label="discharge")
    plt.legend()
    return plt.show()




values = get_value(1646500)
graph = plot_graph(values, values, 1646500)

print(values)



