from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import plotly.graph_objects as go
import plotly.subplots as sp
import plotly.express as px
import pandas as pd
import numpy as np
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from difflib import SequenceMatcher

# initialize chrome webdriver
driver = webdriver.Chrome()
driver.get("https://services.livpartner.com/ci_service/index.php")
driver.maximize_window()

# Login Livpure Dashboard
email_input = driver.find_element(By.ID,"user_name")
email_input.send_keys("1211627207")
password_input = driver.find_element(By.ID,"user_pass")
password_input.send_keys("Apexenterprises@128")
submit_button = driver.find_element(By.NAME,"login")
submit_button.click()
time.sleep(40)
submit_button = driver.find_element(By.NAME,"login")
submit_button.click()

# Data Scraping
open_cases_url = "https://services.livpartner.com/ci_service/index.php/Case_assign?type=ro"
driver.get(open_cases_url)

dropdown = driver.find_element(By.XPATH,"/html/body/section/section/div/div[2]/div/div[1]/label/select[@name = 'myTable_length']")
select_object = Select(dropdown)
select_object.select_by_index(3)

last_page_xpath = '/html/body/section/section/div/div[2]/div/div[4]/span/a[last()]'
last_page = driver.find_element(By.XPATH, last_page_xpath).text
next_button_id = 'myTable_next'
file_datetime = datetime.now().strftime('%d-%m-%Y_%H-%M')
table_data_list = []
count = 0

while count < int(last_page):
  
  table_data = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "myTable")))
  table_html = table_data.get_attribute('outerHTML')
  df_list = pd.read_html(table_html)
  table_data_list.append(df_list[0])
  driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
  time.sleep(4)
  next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, next_button_id)))
  next_button.click()
  time.sleep(5)
  count = count + 1

final_df = pd.concat(table_data_list, ignore_index=True)
excel_file_path = f"files/open_cases_{file_datetime}.xlsx"
final_df["Cust Address"] = final_df["Cust Address"].tolist()

# import area list
area_list = pd.read_excel("area_list.xlsx")
area_list = area_list['area_list'].tolist() 

# add area to respective customer address
def find_matching_job_areas(address):
    matching_areas = []
    address_words = set(address.lower().split())
    
    for area in area_list:
        area_words = set(area.lower().split())
        common_words = address_words.intersection(area_words)
        similarity_ratio = len(common_words) / len(area_words)
        
        if similarity_ratio >= 0.6:
            matching_areas.append(area)
    
    return matching_areas if matching_areas else ["Not Found"]

final_df["job_area_match"] = final_df["Cust Address"].apply(find_matching_job_areas)

#export final modified data
final_df.to_excel(excel_file_path, index=False)

#import final modified data 
df =  pd.read_excel(excel_file_path)

# Add age to respective cases
df['Case Create Date'] = pd.to_datetime(df['Case Create Date'])
current_datetime = datetime.now()
time_difference = current_datetime - df['Case Create Date']
df['time_from_now'] = time_difference.dt.days.astype(str) + " days " + (time_difference.dt.seconds // 3600).astype(str) + " hours"
excel_file_path_aging = f"files/open_aging_{file_datetime}.xlsx"
df.to_excel(excel_file_path_aging, index=False)

# Segregation of open complaints
service_complaint_df = df[df['Case Type'] == 'Service_Complaint'].copy()
service_complaint_df.sort_values(by='time_from_now', ascending=False, inplace=True)
excel_file_path_complaints = f"files/open_cases_complaints_{file_datetime}.xlsx"
service_complaint_df.to_excel(excel_file_path_complaints, index=False)

# Segregation of installation
Install_Req_df = df[df['Case Type'] == 'Install_Req'].copy()
Install_Req_df.sort_values(by='time_from_now', ascending=False, inplace=True)
excel_file_path_installation = f"files/open_cases_installation_{file_datetime}.xlsx"
Install_Req_df.to_excel(excel_file_path_installation, index=False)

# Segregation of PM of last 6 days
PM_Call_df = df[df['Case Type'] == 'PM_Call'].copy()
PM_Call_df.sort_values(by='time_from_now', ascending=False, inplace=True)
PM_Call_df['time_from_now'] = pd.to_timedelta(PM_Call_df['time_from_now'])
filtered_df = PM_Call_df[PM_Call_df['time_from_now'] < pd.Timedelta(days=6)]
excel_file_path_pm = f"files/open_cases_pm_6days_{file_datetime}.xlsx"
filtered_df.to_excel(excel_file_path_pm, index=False)
