import pandas as pd
import requests
import matplotlib.pyplot as plt
import datetime as DT


def get_values(site_code=3179000):
    #2 empty lists that will have the needed values in it
    dates = []
    daily_values = []
    instantanious_values = []
    statistical_values = []

    url_daily = 'https://waterservices.usgs.gov/nwis/dv/?format=json&sites=0{}&period=P7D&siteType=ST&siteStatus=all'.format(site_code)
    url_instantanious = 'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=0{}&period=P7D&siteType=ST&siteStatus=all'.format(site_code)
    url_statistical = 'https://waterservices.usgs.gov/nwis/stat/?format=rdb&sites=0{}&statReportType=daily&statTypeCd=median'.format(site_code)
    
    print("Concatinated URLS = \nDAILY- {}\nINSTANTANIOUS- {}".format(url_daily, url_instantanious))
    
    #to check if the site code is actaully a site code
    url_check = requests.get(url_daily)
    print("HTTP Error code = {}".format(url_check))
    #if satement for variable above ^^^
    if url_check.status_code != 200:
        print("[*] ERROR URL IS BAD")
    
    #a pandas function to open a json
    daily_data = pd.read_json(url_daily)
    instantanious_data = pd.read_json(url_instantanious)
    statistical_data = pd.read_csv(url_statistical, error_bad_lines=False)

    #converting the json into a dataframe fro easy data manipulation
    daily_dataframe = pd.DataFrame(daily_data)
    instantanious_dataframe = pd.DataFrame(instantanious_data)
    statistical_dataframe = pd.DataFrame(statistical_data)
    
    #looping thorugh the dataframe/JSON to get the value and date for the given site and days
    for index in daily_dataframe['value']['timeSeries'][0]['values'][0]['value']:
        #singular value that is in the data retrived by an index key
        raw_value = index['value']
        raw_date = index['dateTime']
        #slicing the long date and time to just get the day in DD format
        prevelant_date = raw_date[8:-13]
        #appending values to the empty lists
        daily_values.append(float(raw_value))
        dates.append(float(prevelant_date))
    
    for index in instantanious_dataframe['value']['timeSeries'][1]['values'][0]['value']:
        raw_value = index['value']
        instantanious_values.append(float(raw_value))
    


    return daily_values, instantanious_values

#def dates():
#    dates = []
#    today = DT.date.today()
#    for days in range(today - DT.timedelta(days=8)):
#        dates.append(days)
#    return dates

while True:
    try:
        site_code = int(input("Site Code- "))
        break
    except ValueError:
        print("[*] PLEASE USE INTEGER")



x_daily, x_instantanious = get_values(site_code)
#y_values = dates()
#print(y_values)

plt.figure("Hydrograph for site 0{} and parameter 00060".format(site_code))
plt.style.use('seaborn-notebook')

plt.ylabel("Discharge, cubic feet per second")
plt.xlabel("past 7 days of water discharge.")
plt.plot(x_instantanious, label="Instantanious Discharge")
plt.legend()

plt.figure("Hydrograph for site {} and parameter 00060 (DAILY VALUES)".format(site_code))
plt.ylabel("Discharge, cubic feet per second")
plt.xlabel("past 7 days of water discharge.")
plt.plot(x_daily, label="Daily Discharge")
plt.legend()
plt.show()
