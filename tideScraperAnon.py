# -*- coding: utf-8 -*-
"""
Web scraper for tidal data from tides4fishing.
Pulls the high and low tidal amplitudes as well as when they occur. Stores data in a CSV.


Matthew Fair
"""
########################
#Begin user inputs

monthChoice     = input("Month (full name): ").capitalize()
yearChoice      = input("Year: ")
continentChoice = input("Continent Code: ")
countryChoice   = input("Country Name: ")
stationChoice   = input('Station name (exact): ').lower()

# End user inputs
########################

## Selenium manipulation to get to the right month of tide data
# imports
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

# set up the chrome page to run in background
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

# set up the driver
DRIVER_PATH = 'C:/Users/Matt/Documents/Python Scripts/Tide Scraper/chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
url = ''.join(['https://xxxxxxxxxxxxxxx.com/',continentChoice,'/',countryChoice,'/',stationChoice])
driver.get(url)


# click calendar to bring up options to change the date
cal_icon = driver.find_element_by_id('boton_calendario_header')
cal_icon.click()
time.sleep(1)

# set the year
cal_years = Select(driver.find_element_by_id('textyear'))
cal_years.select_by_visible_text('yearChoice')
time.sleep(1)

# set the month
cal_years = Select(driver.find_element_by_id('meses'))
cal_years.select_by_visible_text('monthChoice')
time.sleep(1)


# close the calendar
driver.find_element_by_id('calendario_boton_aceptar').click()

# grab page source to pass off to BS
page_source = driver.page_source

# kill the driver, don't need it anymore
driver.quit()

## Beautifulsoup to extract the HTML table and data
# imports
from bs4 import BeautifulSoup
import pandas as pd

# grab page source from selenium
soup = BeautifulSoup(page_source, 'lxml')

# Get the tide data table
gdp = soup.find_all("table", attrs={"id": "tabla_mareas"})
tide_table = gdp[0]

# the head will form our column names
body = tide_table.find_all("tr")

# Head values (Column names) are the first items of the body list
head = body[0:2]     # there are three header rows
body_rows = body[3:] # All other items becomes the rest of the rows

# create headings list
# multilayer headings on page, so manually create it
headings = ['Day', 'Moon Phase', 'Sun Rise/Set', 'Tide1', 'Tide2', 'Tide3', 'Tide4', 'Coefficient', 'Solunar Activity']


# Next is now to loop though the rest of the rows
all_rows = [] # will be a list for list for all rows

# Give up on scraping individual parts of the table and grab the whole thing
for row_num in range(0, len(body_rows), 2): # A row at a time, skip the divider rows
    row = [] # this will old entries for one row
    
    for row_item in body_rows[row_num].find_all("td"): #loop through all row entries
        try:
            row.append(row_item.text.replace('\n', '').replace('\t',''))
        except:
            continue
    
    # append one row to all_rows
    all_rows.append(row)

## Use pandas to make the table less fucking gross
# turn it into a pandas dataframe
df = pd.DataFrame(all_rows, columns=headings)

# get rid of the day of the week and only keep the date
df['Day'] = df['Day'].apply(lambda x: x[0:2]).str.strip()

# set the date as the index
df.set_index('Day',inplace=True)

# drop sun times, moon phase, coeff, and solunar
df.drop(['Sun Rise/Set','Moon Phase','Coefficient','Solunar Activity'],axis=1,inplace=True)

# create empty lists for final data
tide_days  = []
tide_times = []
tide_amps  = []

# iterate through the dataframe rows
for index,row in df.iterrows():
    # write the date
    tide_days.append(index)
    tide_days.append(index)
    tide_days.append(index)
    
    # write the time
    tide_times.append(df['Tide1'][index][0:5].strip())
    tide_times.append(df['Tide2'][index][0:5].strip())
    tide_times.append(df['Tide3'][index][0:5].strip())
    # write the amplitude
    
    tide_amps.append(df['Tide1'][index][-5:-2].strip())
    tide_amps.append(df['Tide2'][index][-5:-2].strip())
    tide_amps.append(df['Tide3'][index][-5:-2].strip())
    
    # check if there was a fourth tide
    if not df['Tide4'][index]:
        continue
    else:
        # write the fourth tide if it's there
        tide_days.append(index)
        tide_times.append(df['Tide4'][index][0:5].strip())
        tide_amps.append(df['Tide4'][index][-5:-2].strip())
    
# split the tide time into hours and minutes
tide_hours, tide_minutes = map(list, zip(*(s.split(':') for s in tide_times)))

# create a dictionary and turn it into a pandas dataframe
dict = {'Day':tide_days,'Hour':tide_hours,'Minute':tide_minutes,'Amplitude':tide_amps}

tide_data = pd.DataFrame(dict)

# write the final dataframe to a csv
tide_data.to_csv(''.join(['tideData_',stationChoice,'_',monthChoice,'_',yearChoice,'.csv']),index=False)




