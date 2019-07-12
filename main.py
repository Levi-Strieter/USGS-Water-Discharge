import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np  
import datetime
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

#optional...to predict the next values using the instantanious dataframe 
def holt_prediction(data, time_steps):
    #setting paramets for the linear regression method, etc.
    fit1 = Holt(data).fit(smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
    #actaul forecast... what will be printed on the graph
    fcast1 = fit1.forecast(time_steps).rename("Holt's linear trend")

    fit2 = Holt(data, exponential=True).fit(smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
    fcast2 = fit2.forecast(time_steps).rename("Exponential trend")

    fit3 = Holt(data, damped=True).fit(smoothing_level=0.8, smoothing_slope=0.2)
    fcast3 = fit3.forecast(time_steps).rename("Additive damped trend")
   
    return fit1, fit2, fit3, fcast1, fcast2, fcast3


#function to get data from the RESTful API and process it into dataframes
def get_data(site_code=3179000):
    
    #urls that will be compiled by site number to contact the RESTful API
    url_daily = 'https://waterservices.usgs.gov/nwis/dv/?format=json&sites=0{}&period=P7D&siteType=ST&siteStatus=all'.format(site_code)
    url_instantanious = 'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=0{}&period=P7D&siteType=ST&siteStatus=all'.format(site_code)
    url_statistical = 'https://waterservices.usgs.gov/nwis/stat/?format=rdb&sites=0{}&statReportType=daily&statTypeCd=median'.format(site_code)

    print("Concatinated URLS = \nDAILY- {}\nINSTANTANIOUS- {}\nSTATISTICAL- {}\n".format(url_daily, url_instantanious, url_statistical))

    #to check if the site code is actaully a site code
    url_check = requests.get(url_daily)
    print("HTTP Error code = {}\n".format(url_check))
    #if satement for variable above ^^^
    if url_check.status_code != 200:
        print("[*] ERROR URL IS BAD")

    #a pandas function to open a json and RDB/CSV format for statistical file
    daily_data = pd.read_json(url_daily)
    instantanious_data = pd.read_json(url_instantanious)
    statistical_data = pd.read_csv(url_statistical, sep="\t", comment="#")

    #converting the json into a dataframe fro easy data manipulation
    daily_dataframe = pd.DataFrame(daily_data)
    instantanious_dataframe = pd.DataFrame(instantanious_data)
    statistical_dataframe = pd.DataFrame(statistical_data, index=None)
    statistical_dataframe = statistical_dataframe.drop(['agency_cd', 'site_no', 'parameter_cd', 'ts_id', 'loc_web_ds', 'begin_yr', 'end_yr', 'count_nu'], axis=1)
    return daily_dataframe, instantanious_dataframe, statistical_dataframe

def get_values(daily_dataframe, instantanious_dataframe, statistical_dataframe):
    #empty lists to store vals in
    daily_values = []
    instantanious_values = []

    #looping thorugh the dataframe/JSON to get the value and date for the given site and days
    for index in daily_dataframe['value']['timeSeries'][0]['values'][0]['value']:
        #singular value that is in the data retrived by an index key
        raw_value = index['value']
        #appending values to the empty lists
        daily_values.append(float(raw_value))
    
    #same thing ^^^
    for index in instantanious_dataframe['value']['timeSeries'][1]['values'][0]['value']:
        raw_value = index['value']
        instantanious_values.append(float(raw_value))

    #a really jank solution to slice the statistical dataframe to get only the vals needed based on the range of days
    start_day = datetime.date(2019, 7, 11)
    current_day = datetime.date.today()
    passed_days = current_day - start_day
    current = 183
    #^^^takes the day I coded this and counts the days till used, then subtracts those days to get an integer to slice the dataframe

    #checking if days have actually passed
    if passed_days > datetime.timedelta(days=0):
        current = 183 + passed_days.days
    else:
        current = 183

    #slicing the data in the pandas dataframe
    future = current + 8
    data = statistical_dataframe['p50_va'][current:future]
    p50_dataframe = pd.Series(data)
    p50_dataframe = p50_dataframe.astype('float64')

    return daily_values, instantanious_values, p50_dataframe

#simple statement to keep the program running untill user gives a integer as an input
while True:
    try:
        site_code = int(input("Site Code- "))
        break
    except ValueError:
        print("[*] PLEASE USE INTEGER")


#return variables from get_data function
daily_dataframe, instantanious_dataframe, statistical_dataframe = get_data(site_code)

#^^^
x_daily, data, p50_vals = get_values(daily_dataframe, instantanious_dataframe, statistical_dataframe)

#putting list values in a series to be processed correctly when sent through matplotlib, obtain right dimensions
y_instantanious = pd.Series(data)

#return variables from holt_predictions function
fit1, fit2, fit3, fcast1, fcast2, fcast3 = holt_prediction(y_instantanious, 50)

#lists to get data to line up when plotting
x_val = [0, 100, 200, 300, 400, 500, 600, 700]
x_val_daily = [0, 100, 200, 300, 400, 500]

#creating a subplot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 9))

#first subplot or actual graph
ax1.set_title("Hydrograph for site # {} and parameter 00060".format(site_code))
ax1.plot(y_instantanious, label="Discharge")
ax1.scatter(x_val, p50_vals, color="y", marker="^", label="statistic discharge")
ax1.legend()
ax1.plot(x_val_daily, x_daily, color="red", marker=".", label="Daily Discharge")

#ssecond subplot for predictions
ax2.set_title("Holt's regression method for predicting future values")
ax = ax2.plot(y_instantanious, color="black")
fit1.fittedvalues.plot(color="blue")
fcast1.plot(color='blue', marker=".", legend=True)
fit2.fittedvalues.plot(color='red')
fcast2.plot(color='red', marker=".", legend=True)
fit3.fittedvalues.plot(color='green')
fcast3.plot(color='green', marker=".", legend=True)

#show it all :)
plt.show()
