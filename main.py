import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np  
import datetime
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

def holt_prediction(data, time_steps):
    fit1 = Holt(data).fit(smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
    fcast1 = fit1.forecast(time_steps).rename("Holt's linear trend")

    fit2 = Holt(data, exponential=True).fit(smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
    fcast2 = fit2.forecast(time_steps).rename("Exponential trend")

    fit3 = Holt(data, damped=True).fit(smoothing_level=0.8, smoothing_slope=0.2)
    fcast3 = fit3.forecast(time_steps).rename("Additive damped trend")
   
    return fit1, fit2, fit3, fcast1, fcast2, fcast3

def get_values(site_code=3179000):
    #3 empty lists that will have the needed values in
    daily_values = []
    instantanious_values = []
    statistical_values = []

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
    
    #a pandas function to open a json
    daily_data = pd.read_json(url_daily)
    instantanious_data = pd.read_json(url_instantanious)
    statistical_data = pd.read_csv(url_statistical, sep="\t", comment="#")

    #converting the json into a dataframe fro easy data manipulation
    daily_dataframe = pd.DataFrame(daily_data)
    instantanious_dataframe = pd.DataFrame(instantanious_data)
    statistical_dataframe = pd.DataFrame(statistical_data, index=None)   
    statistical_dataframe = statistical_dataframe.drop(['agency_cd', 'site_no', 'parameter_cd', 'ts_id', 'loc_web_ds', 'begin_yr', 'end_yr', 'count_nu'], axis=1)
    
    #looping thorugh the dataframe/JSON to get the value and date for the given site and days
    for index in daily_dataframe['value']['timeSeries'][0]['values'][0]['value']:
        #singular value that is in the data retrived by an index key
        raw_value = index['value']
        #appending values to the empty lists
        daily_values.append(float(raw_value))
    
    for index in instantanious_dataframe['value']['timeSeries'][1]['values'][0]['value']:
        raw_value = index['value']
        instantanious_values.append(float(raw_value))

    
    start_day = datetime.date(2019, 7, 11)
    current_day = datetime.date.today()
    passed_days = current_day - start_day
    current = 183

    if passed_days > datetime.timedelta(days=0):
        current = 183 + passed_days
    else:
        current = 183

    future = current + 8
    data = statistical_dataframe['p50_va'][current:future]
    p50_dataframe = pd.Series(data)
    p50_dataframe = p50_dataframe.astype('int64')

    return daily_values, instantanious_values, p50_dataframe

while True:
    try:
        site_code = int(input("Site Code- "))
        break
    except ValueError:
        print("[*] PLEASE USE INTEGER")


x_daily, data, p50_vals = get_values(site_code)


y_instantanious = pd.Series(data)
x_val = [0, 100, 200, 300, 400, 500, 600, 700]


fit1, fit2, fit3, fcast1, fcast2, fcast3 = holt_prediction(y_instantanious, 50)


plt.figure("Hydrograph for site 0{} and parameter 00060".format(site_code))
plt.style.use('seaborn-notebook')

plt.ylabel("Discharge, cubic feet per second")
plt.xlabel("past 7 days of water discharge.")  
plt.plot(y_instantanious, label="Instantanious Discharge")
plt.scatter(x_val, p50_vals, color="y", marker="^", label="median daily statistic")
plt.legend()

plt.figure("Hydrograph for site 0{} and parameter 00060 (DAILY VALUES)".format(site_code))
plt.ylabel("Discharge, cubic feet per second")
plt.xlabel("past 7 days of water discharge.")
plt.plot(x_daily, label="Daily Discharge")
plt.legend()
plt.show()

print("[*] NOW PLOTTING PREDICTED WATER DISCHARGE BASED ON HOLT REGRESSIONAL METHOD [*]")

ax = y_instantanious.plot(color="black", figsize=(12,8))
fit1.fittedvalues.plot(ax=ax, color='blue')
fcast1.plot(ax=ax, color='blue', marker=".", legend=True)
fit2.fittedvalues.plot(ax=ax, color='red')
fcast2.plot(ax=ax, color='red', marker=".", legend=True)
fit3.fittedvalues.plot(ax=ax, color='green')
fcast3.plot(ax=ax, color='green', marker=".", legend=True)
plt.show()
