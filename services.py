from config import Config as environ
import calendar
from dataAccess import DataAccess
from dataTransform import DataTransform
import smtplib
from flask import session
from threading import Thread
import redis
from queue import Queue
from flask import render_template
import pandas as pd
from numpy import array_split

calendar.setfirstweekday(calendar.SUNDAY)
# redis_cnxn = redis.Redis(host='localhost', port=6379, db=0, password = environ.REDIS_PASSWORD)
da = DataAccess()
    # redis_cnxn)
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
        session['accountid'] = int(account_id)
        return (True, None)
    else:
        session['logged_in'] = False
        session['accountid'] = None
        return (False, 'Invalid username or password')
        
def prepare_activity_list(session_df, result_queue, desc_order):
    activity_list = dt.prepare_multiple_activities(session_df, desc_order)
    result_queue.put((activity_list, 'activity_list'))
    return    

def get_activity_info(session_df):
    result_queue = Queue()
    num_threads = 5
    threads = []
    session_df_splits = array_split(session_df, num_threads)
    for i in range(num_threads):
        thread = Thread(target=prepare_activity_list, args=(session_df_splits[i], result_queue))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    results = []
    while not result_queue.empty():
        queue_item = result_queue.get()
        results += queue_item[0]
    return results

def prepare_lap_list(lap_df, activity_id_list, result_queue):
    lap_list = dt.prepare_lap_info(lap_df, activity_id_list)
    result_queue.put((lap_list, 'lap_list'))
    return

def get_lap_list(lap_df, activity_id_list):
    result_queue = Queue()
    num_threads = 10
    threads = []
    lap_df_splits = array_split(lap_df, num_threads)
    activity_id_list_splits = array_split(activity_id_list, num_threads)
    for i in range(num_threads):
        thread = Thread(target=prepare_lap_list, args=(lap_df_splits[i], activity_id_list_splits[i], result_queue))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    results = []
    while not result_queue.empty():
        queue_item = result_queue.get()
        results += queue_item[0]
    return results

def prepare_record_html_list(record_info, activity_id_list, result_queue):
    record_html_list = dt.prepare_record_info(record_info, activity_id_list)
    result_queue.put((record_html_list, 'record_html_list'))
    return

def prepare_record_html_list_threads(record_info, activity_id_list):
    result_queue = Queue()
    num_threads = 10
    threads = []
    record_info_splits = array_split(record_info, num_threads)
    activity_id_list_splits = array_split(activity_id_list, num_threads)
    for i in range(num_threads):
        thread = Thread(target=prepare_record_html_list, args=(record_info_splits[i], activity_id_list_splits[i], result_queue))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    results = []
    while not result_queue.empty():
        queue_item = result_queue.get()
        results += queue_item[0]
    return results
        
def prepare_all_info_threads(session_df, lap_df, record_info, desc_order=False):
    result_queue = Queue()
    activity_thread = Thread(target=prepare_activity_list, args=(session_df, result_queue, desc_order))
    lap_thread = Thread(target=prepare_lap_list, args=(lap_df, session_df['activity_id'].to_list(), result_queue))
    record_thread = Thread(target=prepare_record_html_list, args=(record_info, session_df['activity_id'].to_list(), result_queue))
    threads = [activity_thread, lap_thread, record_thread]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return_dict = {}
    while not result_queue.empty():
        queue_item = result_queue.get()
        return_dict[queue_item[1]] = queue_item[0]
    return return_dict
    
def single_date(date_str):
    session_df, lap_df, record_df = da.get_activity_info_by_date(pd.to_datetime(date_str).date(), session['accountid'])
    if len(session_df) == 0:
        print("NO ACTIVITY FOUND")
        return (False, 'No activities found')
    print("ACTIVITY FOUND")
    date_title = pd.to_datetime(date_str).strftime('%B %d %Y')
    all_info = prepare_all_info_threads(session_df, lap_df, record_df)
    all_info['date_title'] = date_title
    return (True, all_info)

def month_detail(month, year):
    start_date = pd.Timestamp(f'{year}-{month}-01')
    end_date = pd.Timestamp(f'{year}-{month}-01') + pd.offsets.MonthEnd(0)
    session_df, lap_df, record_df = da.get_activity_info_by_date_range(start_date.date(), end_date.date(), session['accountid'])
    if len(session_df)==0:
        print("NO ACTIVITY FOUND")
        return (False, 'No activities found')
    print("ACTIVITY FOUND")
    month_string = pd.to_datetime(f'{month}/01/{year}').strftime('%B %Y')    
    all_info = prepare_all_info_threads(session_df, lap_df, record_df)
    all_info['date_title'] = month_string
    return (True, all_info)
    
def get_single_activity_info(activity_id): 
    session_info, lap_info, record_info = da.get_activity_by_id(activity_id)
    if len(session_info) == 0:
        return (False, 'No activity found')
    all_info = prepare_all_info_threads(session_info, lap_info, record_info)
    return (True, all_info)

def prepare_rendered_info(all_info):
    templates = []
    for activity, lap_html, folium_map, i in zip(all_info['activity_list'], all_info['lap_list'], all_info['record_html_list'], list(range(len(all_info['activity_list'])))):
        template = render_template('_activity.html', activity=activity, lap_html=lap_html, folium_map=folium_map, i=i)
        templates.append(template)
    return templates

def get_home_page_posts(offset, limit, sport, render=False):
    session_df, lap_df, record_df = da.get_recent_posts(session['accountid'], offset, limit, sport)
    if len(session_df) == 0:
        return (False, 'No activities found')
    all_info = prepare_all_info_threads(session_df, lap_df, record_df, desc_order=True)
    if render:
        all_info = prepare_rendered_info(all_info)
    return (True, all_info)

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
        activity_info = da.get_calendar_info(year, month, session['accountid'])
        if len(activity_info) > 0:
            cal = dt.prepare_calendar_info(activity_info, cal)
        return (True, (cal, month_string, month, year, current_month))
    except Exception as e:
        return (False, str(e))
        
def search_for_editing(input, input_type):
    date = input if input_type == 'date' else None
    title = input if input_type == 'title' else None
    try:
        search_results = da.search_activities_for_editing(date, title, session['accountid'])
        search_results['total_time'] = search_results['total_time'].apply(lambda x: dt.time_seconds_to_string(x))
        return (True, search_results.to_dict(orient='records'))
    except Exception as e:
        return (False, str(e))
 
 
# {'activity_id': '11947108956', 'activity_title': 'Running Activity', 'description': '', 'start_time': '7/21/2024 2:02 pm', 'display_sport': 'Running', 'total_time': '47:51', 'total_distance': '7.01 mi.'}   
def merge_check_process(activity1, activity2):
    try:
        date1 = pd.to_datetime(activity1['start_time']).date()
        date2 = pd.to_datetime(activity2['start_time']).date()
        if date1 != date2:
            day_diff = abs((date1 - date2).days)
            return (True, {'date_diff': day_diff})
        sport1 = activity1['display_sport']
        sport2 = activity2['display_sport']
        if sport1 != sport2:
            return (True, {'sport_diff': (sport1, sport2)})
        return (True, '')
    except Exception as e:
        return (False, str(e))