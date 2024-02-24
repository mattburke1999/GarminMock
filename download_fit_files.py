from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import os
import json
import psycopg2
import traceback
import time
import pandas as pd
load_dotenv()

def start_driver():
    profile_path = r'C:\Users\mattb\GarminProfile'

    # Create a Chrome Options object to specify the profile
    chrome_options = Options()
    chrome_options.add_argument(f'user-data-dir={profile_path}')
    # chrome_options.add_argument('--headless')

    # Set up the Chrome WebDriver with the specified options
    # Using webdriver-manager to manage the driver binary for ease of use
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('https://www.strava.com/login')
    return driver
def login(driver):
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(os.getenv('strava_email'))
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(os.getenv('strava_password'))
    driver.find_element(By.XPATH, '//*[@id="login-button"]').click()
def go_to_activities(driver):
    driver.get('https://www.strava.com/athlete/training')
    return

def connect_to_postgres():
    db_params = json.loads(os.environ.get('PostgreSQL'))
    cnxn = psycopg2.connect(**db_params)
    cnxn.autocommit = True
    return cnxn
def find_max_date():
    cnxn = connect_to_postgres()
    query = 'select max(start_time) "start_time" from raw_garmin_data_session'
    max_start = pd.read_sql_query(query, cnxn)['start_time'][0]
    cnxn.close()
    day = max_start.strftime('%a')
    month_int = max_start.month
    day_int = max_start.day
    year = max_start.year
    date_string = f'{day}, {month_int}/{day_int}/{year}'
    return date_string
def get_activity_dates(driver, max_start):
    act_dict = {'date':[], 'link':[]}
    for i in range(1,30):
        try:
            date = driver.find_element(By.XPATH, f'//*[@id="search-results"]/tbody/tr[{i}]/td[2]')
            link = driver.find_element(By.XPATH, f'//*[@id="search-results"]/tbody/tr[{i}]/td[3]/a').get_attribute('href')
            max_start_date = pd.to_datetime(max_start.split(', ')[1])
            activity_date = pd.to_datetime(date.text.split(', ')[1])
            if date.text == max_start or activity_date < max_start_date:
                break
            act_dict['date'].append(date.text)
            act_dict['link'].append(link)
            print(f'sucess for {date.text}')
        except:
            print(traceback.format_exc())
            break
            
    return act_dict
def rename_file(link):
    activity_id = link.replace('https://www.strava.com/activities/', '')
    new_filename = f'activitie_{activity_id}.fit'
    newUploads = os.listdir(r"C:\Users\mattb\OneDrive\Documents\LoginTEST\garmin data\NEW_UPLOADS")
    files_to_change = [file for file in newUploads if not file.startswith('activitie_') and file.endswith('.fit')]
    newFileNames = []
    if len(files_to_change) > 1:
        print('more than one file to change')
        for i in range(len(files_to_change)):
            newFileNames.append(f'{new_filename}_{i}.fit')
    elif len(files_to_change) == 1:
        newFileNames = [new_filename]
    else:
        print('no files to change')
    for i in range(len(files_to_change)):
        folder = r"C:\Users\mattb\OneDrive\Documents\LoginTEST\garmin data\NEW_UPLOADS"
        os.rename(f'{folder}\{files_to_change[i]}', f'{folder}\{newFileNames[i]}')
    return
def download_activities(driver, act_dict):
    for i in range(len(act_dict['link'])):
        driver.get(f"{act_dict['link'][i]}/export_original")
        print(f'downloading {act_dict["date"][i]}')
        time.sleep(2)
        rename_file(act_dict['link'][i])
        time.sleep(2)
    return
def close_driver(driver):
    driver.close()
    driver.quit()
    return

if __name__ == '__main__':
    driver = start_driver()
    login(driver)
    print('logged in')
    go_to_activities(driver)
    max_start = find_max_date()
    print('got max date')
    time.sleep(2)
    act_dict = get_activity_dates(driver, max_start)
    print('found activities to download')
    download_activities(driver, act_dict)
    print('downloaded activities')
    close_driver(driver)
