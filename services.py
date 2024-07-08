from config import Config as environ
import calendar
from dataAccess import DataAccess
from dataTransform import DataTransform
import smtplib
from flask import session
from threading import Thread
import redis
from queue import Queue
import json
import pandas as pd
import traceback

calendar.setfirstweekday(calendar.SUNDAY)
redis_cnxn = redis.Redis(host='localhost', port=6379, db=0, password = environ.REDIS_PASSWORD)
da = DataAccess(redis_cnxn)
dt = DataTransform()

def send_registration_email(email, firstname, lastname):
    gmail_user = environ.GMAIL_USER
    gmail_password = environ.GMAIL_PASSWORD
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Upgrade the connection to secure
    server.login(gmail_user, gmail_password)
    
    subject = 'Welcome to GarminMockup'
    message = f'Hello {firstname} {lastname},\n\nYou have successfully registered an account with GarminMockup.'

    # Creating the email content
    email_body = f"Subject: {subject}\n\n{message}"

    # Sending the email
    server.sendmail(gmail_user, email, email_body)
    print("Email sent successfully!")

    # Closing the server connection
    server.quit()
    return

def register_user(firstname, lastname, username, password, result_queue):
    try:
        da.register_user(firstname, lastname, username, password)
        result_queue.put((True, ''))
    except Exception as e:
        result_queue.put((False, str(e)))
    
def register_process(firstname, lastname, email, username, password):
    result_queue = Queue()
    
    register_thread = Thread(target=register_user, args=(firstname, lastname, username, password, result_queue))
    register_thread.start()
    
    send_email_thread = Thread(target=send_registration_email, args=(email, firstname, lastname))
    send_email_thread.start()
    
    register_thread.join()
    
    success, error = (False, "Unknown error")
    while not result_queue.empty():
        success, error = result_queue.get()
    return success, error

def login_process(username, password):
    account_id = da.verify_user(username, password)
    if account_id is not None:
        session['logged_in'] = True
        return (True, None)
    else:
        session['logged_in'] = False
        return (False, 'Invalid username or password')
        
def prepare_activity_list(session_df, result_queue):
    activity_list = dt.prepare_multiple_activities(session_df)
    result_queue.put((activity_list, 'activity_list'))
    return

def prepare_lap_html_list(lap_df, activity_id_list, result_queue):
    lap_html_list = dt.prepare_lap_info(lap_df, activity_id_list)
    result_queue.put((lap_html_list, 'lap_html_list'))
    return

def prepare_record_html_list(record_info, activity_id_list, result_queue):
    record_html_list = dt.prepare_record_info(record_info, activity_id_list)
    result_queue.put((record_html_list, 'record_html_list'))
    return
    
def single_date(date_str):
    session_df, lap_df, record_info = da.get_activity_info_by_date(pd.to_datetime(date_str).date())
    if len(session_df) == 0:
        print("NO ACTIVITY FOUND")
        return (False, 'No activity found')
    print("ACTIVITY FOUND")
    activity_thread = Thread(target=prepare_activity_list, args=(session_df,None))
    lap_thread = Thread(target=prepare_lap_html_list, args=(lap_df, list(set(session_df['activity_id'])), None))
    record_thread = Thread(target=prepare_record_html_list, args=(record_info, list(set(session_df['activity_id'])), None))
    threads = [activity_thread, lap_thread, record_thread]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
 
    session['date_title'] = pd.to_datetime(date_str).strftime('%B %d %Y')
    return (True, None)

def month_detail(month, year):
    start_date = pd.Timestamp(f'{year}-{month}-01')
    end_date = pd.Timestamp(f'{year}-{month}-01') + pd.offsets.MonthEnd(0)
    session_df, lap_df, record_df = da.get_activity_info_by_date_range(start_date.date(), end_date.date())
    if len(session_df)==0:
        print("NO ACTIVITY FOUND")
        return (False, 'No activity found')
    print("ACTIVITY FOUND")
    result_queue = Queue()
    activity_thread = Thread(target=prepare_activity_list, args=(session_df, result_queue))
    lap_thread = Thread(target=prepare_lap_html_list, args=(lap_df, list(set(session_df['activity_id'])), result_queue))
    record_thread = Thread(target=prepare_record_html_list, args=(record_df, list(set(session_df['activity_id'])), result_queue))
    threads = [activity_thread, lap_thread, record_thread]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
        
    while not result_queue.empty():
        queue_item = result_queue.get()
        if queue_item[1] == 'activity_list':
            print(f'ACTIVITY LIST: {queue_item[0]}')
        session[queue_item[1]] = da.create_cookie(json.dumps(queue_item[0]))
        
    month_string = pd.to_datetime(f'{month}/01/{year}').strftime('%B %Y')
    session['date_title'] = month_string
    return (True, None)
 
def get_item_from_redis(item_name, result_queue, item_id): 
    result_queue.put((json.loads(da.get_cookie_value(item_id)), item_name))
    return
 
def get_multiple_activity_info():
    try:
        result_queue = Queue()
        item_names = ['activity_list', 'lap_html_list', 'record_html_list']
        threads = []
        for item in item_names:
            thread = Thread(target=get_item_from_redis, args=(item, result_queue, session[item]))
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
        activity_infos = {}
        while not result_queue.empty():
            print("GETTING RESULTS FROM QUEUE")
            queue_item = result_queue.get()
            activity_infos[queue_item[1]] = queue_item[0]
        print(f'ACTIVITY INFOS: {activity_infos}')
        return (True, (activity_infos['activity_list'], activity_infos['lap_html_list'], activity_infos['record_html_list']))
    except Exception:
        return (False, traceback.format_exc())
    
def get_single_activity_info(activity_id): 
    session_info, lap_info, record_info = da.get_activity_by_id(activity_id)
    if len(session_info) == 0:
        return (False, 'No activity found')
    result_queue = Queue()
    activity_thread = Thread(target=prepare_activity_list, args=(session_info, result_queue))
    lap_thread = Thread(target=prepare_lap_html_list, args=(lap_info, [activity_id], result_queue))
    record_thread = Thread(target=prepare_record_html_list, args=(record_info, [activity_id], result_queue))
    threads = [activity_thread, lap_thread, record_thread]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    activity_info = {}
    while not result_queue.empty():
        queue_item = result_queue.get()
        activity_info[queue_item[1]] = queue_item[0][0]
    
    activity_dict = activity_info['activity_list']
    lap_html = activity_info['lap_html_list']
    folium_map = activity_info['record_html_list']
    return (True, (activity_dict, lap_html, folium_map))

def get_month_dates(month, year):
    today = pd.Timestamp.now()
    current_month = today.strftime('%B %Y')
    if month == 0 and year == 0:
        print('No month or year')
        month = today.month
        year = today.year
        month_string = current_month
    else:
        print("MONTH AND YEAR FOUND")
        if month == 0:
            month = 12
            year -= 1
        elif month == 13:
            month = 1
            year += 1
        month_string = pd.to_datetime(f'{month}/01/{year}').strftime('%B %Y')
    return month, year, month_string, current_month

def get_calendar_info():
    try: 
        month = session.get('month', 0)
        session['month'] = 0
        year = session.get('year', 0)
        session['year'] = 0
        month, year, month_string, current_month = get_month_dates(month, year)
        # Generate calendar data for current month
        cal = calendar.monthcalendar(year, month)
        cal = [['--' if day == 0 else day for day in week] for week in cal] # add day numbers to calendar
        cal = [[(day, []) for day in week] for week in cal] # change each day to a tuple with an empty list
        activity_info = da.get_calendar_info(year, month)
        if len(activity_info) > 0:
            cal = dt.prepare_calendar_info(activity_info, cal)
        return (True, (cal, month_string, month, year, current_month))
    except Exception as e:
        return (False, str(e))
        