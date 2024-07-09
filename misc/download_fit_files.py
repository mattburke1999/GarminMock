from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
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
    # service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome( options=chrome_options)
    driver.get('https://www.strava.com/login')
    return driver

def login(driver):
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(os.getenv('strava_email'))
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(os.getenv('strava_password'))
    driver.find_element(By.XPATH, '//*[@id="login-button"]').click()
    return

def go_to_activities(driver):
    driver.get('https://www.strava.com/athlete/training')
    return

def connect_to_postgres():
    db_params = json.loads(os.environ.get('PostgreSQL_desktop'))
    cnxn = psycopg2.connect(**db_params)
    cnxn.autocommit = True
    return cnxn

def find_max_date():
    cnxn = connect_to_postgres()
    query = 'select max(start_time) "start_time" from raw_garmin_data_session'
    max_start = pd.read_sql_query(query, cnxn)['start_time'][0]
    cnxn.close()
    return max_start.tz_localize(None)

def get_activity_dates(driver, max_start_date, activities = []):
    time.sleep(3)
    max_date = pd.to_datetime('2024-05-09')
    min_date = pd.to_datetime('2024-03-13')
    new_activities = driver.find_elements(By.CLASS_NAME, 'training-activity-row') # find all activities (rows)
    # extract (date, link) from each row
    new_activities = [(pd.to_datetime(activity.find_element(By.CLASS_NAME, 'view-col.col-date').text.split(', ')[1]), activity.find_element(By.CLASS_NAME, 'view-col.col-title').find_element(By.TAG_NAME, 'a').get_attribute('href')) for activity in new_activities]
    new_activities.sort(key=lambda x: x[0]) # sort by date
    if len(new_activities) > 0:
        oldest_activity_date = new_activities[0][0]
        print(f'OLDEST ACTIVITY DATE: {oldest_activity_date}')
        print(f'Min: {min_date}, Max: {max_date}')
        if oldest_activity_date > min_date and oldest_activity_date < max_date:
            print('CONDITION 1')
            new_activities = [activity for activity in new_activities if activity[0] > min_date and activity[0] < max_date] # filter out activities before min_date and after max_date
            activities += new_activities
            driver.find_element(By.XPATH, '/html/body/div[2]/nav/div/ul/li[2]/button').click()
            return get_activity_dates(driver, max_start_date, activities) # repeat with next page
        elif oldest_activity_date <= min_date:
            print('CONDITION 2')
            return activities
        else: # oldest_activity_date >= max_date
            print('CONDITION 3')
            driver.find_element(By.XPATH, '/html/body/div[2]/nav/div/ul/li[2]/button').click() # next page
            return get_activity_dates(driver, max_start_date, activities) # repeat with next page
        
        # if oldest_activity_date < max_start_date:
        #     new_activities = [activity for activity in new_activities if activity[0] >= max_start_date] # filter out activities before max_date
        #     activities += new_activities
        #     return activities # no need to go to next page
        # else:  # oldest_activity_date >= max_start_date
        #     driver.find_element(By.XPATH, '/html/body/div[2]/nav/div/ul/li[2]/button').click() # next page
        #     return get_activity_dates(driver, max_start_date, activities + new_activities) # repeat with next page
    return activities

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

def download_activities(driver, activities):
    # activities: list(tuple(date, link))
    for activity in activities:
        driver.get(f"{activity[1]}/export_original")
        print(f'downloading {activity[0]}')
        time.sleep(2)
        rename_file(activity[1])
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
    max_start_date = find_max_date()
    print('got max date')
    activities = get_activity_dates(driver, max_start_date)
    print('found activities to download')
    download_activities(driver, activities)
    print('downloaded activities')
    close_driver(driver)
