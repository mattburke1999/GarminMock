from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
import pandas as pd
import warnings
from functools import wraps
import psycopg2
import bcrypt
import smtplib
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import os
import json
load_dotenv()

app = Flask(__name__)
mile_dist = 1609.344

app.config['SECRET_KEY'] = 'your_secret_key_here'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session['logged_in'] == False:
            print("NOT LOGGED IN")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def connect_to_postgres():
    db_params = json.loads(os.environ.get('PostgreSQL'))
    cnxn = psycopg2.connect(**db_params)
    cnxn.autocommit = True
    return cnxn

def verify_user(username, password):
    cnxn = connect_to_postgres()
    query = 'select * from public.accounts where "userid" = %s'
    users = pd.read_sql_query(query, cnxn, params=[username])
    cnxn.close()
    stored_password_bytes = bytes(users['password'].iloc[0])
    if not users.empty:
        provided_password_bytes = password.encode('utf-8')
        # Verify the password
        if bcrypt.checkpw(provided_password_bytes, stored_password_bytes):
            return users['accountid'].iloc[0]  # Login successful
        else:
            return None  # Password does not match
    else:
        return None

def get_new_account_id():
    cnxn = connect_to_postgres()
    query = 'select max(AccountId) as max from public.accounts'
    df = pd.read_sql_query(query, cnxn)
    cnxn.close()
    if len(df)==0 or df.iloc[0]['max'] is None:
        return 1
    return int(int(df.iloc[0]['max']) + 1)

def hash_password(password):
    # Convert the password to bytes
    password_bytes = password.encode('utf-8')
    # Generate a salt and hash the password
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed

def register_user(firstname, lastname, userid, password):
    cnxn = connect_to_postgres()
    query = '''
        insert into public.accounts("accountid", "firstname", "lastname", "userid", "password", "creationdate")
        values(%s,%s,%s,%s,%s, current_timestamp)    
    '''
    params = [get_new_account_id(), firstname, lastname, userid, hash_password(password)]
    cnxn.cursor().execute(query, params)
    cnxn.commit()
    cnxn.close()
    return

def send_registration_email(email, firstname, lastname):
    gmail_user = os.environ.get('gmail_user')
    gmail_password = os.environ.get('gmail_password')
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

def create_cookie(value):
    cnxn = connect_to_postgres()
    query = 'insert into public.cookies(value) VALUES (%s) returning id'
    cursor = cnxn.cursor()
    cursor.execute(query, (value,))
    cnxn.commit()
    id = cursor.fetchone()[0]
    cnxn.close()
    return id

def delete_cookie(id):
    cnxn = connect_to_postgres()
    query = 'delete from public.cookies where id = %s'
    cursor = cnxn.cursor()
    cursor.execute(query, (id,))
    cnxn.commit()
    cnxn.close()
    return

def get_cookie_value(id):
    cnxn = connect_to_postgres()
    query = 'select value from public.cookies where id = %s'
    cursor = cnxn.cursor()
    cursor.execute(query, (id,))
    value = cursor.fetchone()[0]
    cnxn.close()
    
    delete_cookie(id)
    return value   

def time_seconds_to_string(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    if hours == 0:
        return f'{minutes} min {round(seconds,3)} sec'
    elif hours == 1:
        return f'{hours} hr {minutes} min {round(seconds,3)} sec'
    else:
        return f'{hours} hrs {minutes} min {round(seconds,3)} sec'

def get_activity_info_by_date(date):
    cnxn = connect_to_postgres()
    cnxn.autocommit = False
    cursor = cnxn.cursor()
    cursor.callproc('get_activity_info_by_date', (date,))

    session_curs, lap_curs = cursor.fetchone()

    session_info = pd.read_sql_query(f'FETCH ALL IN "{session_curs}"', cnxn)
    session_info = session_info
    lap_info = pd.read_sql_query(f'FETCH ALL IN "{lap_curs}"', cnxn)

    cnxn.close()
    return session_info, lap_info

def get_activity_info_by_date_range(start_date, end_date):
    cnxn = connect_to_postgres()
    cnxn.autocommit = False
    cursor = cnxn.cursor()
    cursor.callproc('get_activity_info_by_date_range', (start_date, end_date))

    session_curs, lap_curs = cursor.fetchone()

    session_info = pd.read_sql_query(f'FETCH ALL IN "{session_curs}"', cnxn)
    session_info = session_info
    lap_info = pd.read_sql_query(f'FETCH ALL IN "{lap_curs}"', cnxn)
    cnxn.close()
    return session_info, lap_info

def prepare_running(activity, activity_dict):
    distance = activity['total_distance']
    activity_dict['Distance'] = float(round(distance/mile_dist, 3))
    pace = activity['total_time'] / (distance/mile_dist)
    activity_dict['Pace'] = time_seconds_to_string(pace)
    elapsed_pace = activity['total_elapsed_time'] / (distance/mile_dist)
    activity_dict['Elapsed Pace'] = time_seconds_to_string(elapsed_pace)
    activity_dict['Avg Cadence'] = int(activity['avg_running_cadence'])
    activity_dict['Max Cadence'] = int(activity['max_running_cadence'])
    activity_dict['Steps'] = int(activity['total_strides'])
    stride_length = activity['total_distance'] / activity['total_strides']
    activity_dict['Avg Stride Length'] = round(stride_length, 2)
    return activity_dict

def prepare_cycling(activity, activity_dict):
    distance = activity['total_distance']
    activity_dict['Distance'] = float(round(distance/mile_dist, 3))
    total_time = activity['total_time']
    total_elapsed_time = activity['total_elapsed_time']
    speed = (distance / mile_dist) / (total_time / 3600)
    elapsed_speed = (distance / mile_dist) / (total_elapsed_time / 3600)
    activity_dict['Speed'] = float(round(speed, 2))
    activity_dict['Elapsed Speed'] = float(round(elapsed_speed, 2))
    return activity_dict

def prepare_rowing(activity, activity_dict):
    activity_dict['Distance'] = float(activity['total_distance'])
    #calculate pace min:sec/500m
    total_time = activity['total_time']
    elapsed_time = activity['total_elapsed_time']
    distance = activity['total_distance']
    pace = (total_time) / (distance / 500) if distance != 0 else 0
    elapsed_pace = (elapsed_time) / (distance / 500) if distance != 0 else 0
    activity_dict['Pace'] = time_seconds_to_string(pace)
    activity_dict['Elapsed Pace'] = time_seconds_to_string(elapsed_pace)
    total_cycles = activity['total_cycles']
    activity_dict['Total Strokes'] = int(total_cycles)
    total_time = activity['total_time']
    activity_dict['Stroke Rate'] = float(round((total_cycles / (total_time / 60)),2))
    elapsed_time = activity['total_elapsed_time']
    activity_dict['Elapsed Stroke Rate'] = float(round((total_cycles / (elapsed_time / 60)),2))
    return activity_dict

def lap_dfs_to_htmls(lap_df):
    activity_ids = lap_df['activity_id'].unique()
    lap_html_list = []
    for activity_id in activity_ids:
        lap = lap_df[lap_df['activity_id'] == activity_id]
        if len(lap) == 0:
            lap_html_list.append(None)
        else:
            lap = lap.drop('activity_id', axis=1)
            lap_html = lap.to_html(index=False).replace(' style="text-align: right;"','').replace(' border="1"','')
            for col in lap.columns:
                lap_html = lap_html.replace(f'<th>{col}</th>', f'<th class="colTitle">{col}</th>')
            lap_html_list.append(lap_html)
    return lap_html_list

def time_seconds_to_string_lap(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    if hours == 0:
        if seconds < 10:
            return f'{minutes}:0{round(seconds,3)}'
        return f'{minutes}:{round(seconds,3)}'
    else:
        if seconds < 10:
            return f'{hours}:{minutes}:0{round(seconds,3)}'
        return f'{hours}:{minutes}:{round(seconds,3)}'

def prepare_lap_info(df):
    cols = df.columns.tolist()
    df['lap'] = df['lap_num']
    df['distance'] = df['total_distance'].apply(lambda x: round(x/mile_dist, 2))
    df['duration'] = df['total_time'].apply(lambda x: time_seconds_to_string_lap(x))
    df['elapsed time'] = df['total_elapsed_time'].apply(lambda x: time_seconds_to_string_lap(x))
    df['avg_speed'] = df['avg_speed'].apply(lambda x: round(mile_dist/(60*x), 2) if x > 0 else 0)
    df['pace_calc'] = df.apply(lambda row: row['total_time'] / (row['total_distance'] / mile_dist) if row['total_distance'] != 0 else 0, axis=1)    # set df['pace'] = df['avg_speed'] if avg_speed > 0 else pace_calc
    df['pace'] = df.apply(lambda row: row['avg_speed'] if row['avg_speed'] > 0 else row['pace_calc'], axis=1)
    df['pace'] = df['pace'].apply(lambda x: time_seconds_to_string_lap(x))
    df['max_speed'] = df['max_speed'].apply(lambda x: round(mile_dist/(60*x), 2) if x > 0 else 0)
    df['best pace'] = df['max_speed'].apply(lambda x: x if x > 0 else 0)
    df['avg hr'] = df['avg_hr']
    df['max hr'] = df['max_hr']
    df['avg cadence'] = df['avg_running_cadence']
    df['max cadence'] = df['max_running_cadence']
    df['steps'] = df['total_strides']
    df['avg stride length'] = df.apply(lambda row: round(row['total_distance'] / row['total_strides'], 2) if row['total_strides'] > 0 else 0, axis=1)
    df['calories'] = df['total_calories']
    df['total ascent'] = df['total_ascent']
    df['total descent'] = df['total_descent']
    cols.append('pace_calc')
    cols.remove('activity_id')
    df = df.sort_values(by=['start_time', 'lap'])
    df = df.drop(cols, axis=1)
    html_list = lap_dfs_to_htmls(df)
    return html_list

def prepare_multiple_activities(df):
    activity_list = []
    df = df.sort_values(by=['start_time'])
    for i in range(len(df)):
        activity_dict = {}
        activity = df.iloc[i]
        activity_dict['Activity Title'] = activity['activity_title'].title()
        activity_dict['Description'] = activity['description']
        activity_dict['activity_id'] = activity['activity_id']
        start_time = activity['start_time']
        date_part = start_time.strftime('%A, %B %d')
        time_part = start_time.strftime('%I:%M %p')
        activity_dict['date_edit'] = start_time.strftime('%Y-%m-%d')
        activity_dict['time_edit'] = start_time.strftime('%H:%M')
        if time_part[0] == '0':
            time_part = time_part[1:]
        activity_dict['Date'] = f'{date_part} @ {time_part}'
        sport = activity['sport']
        capitalSport = sport.title()        
        activity_dict['Sport'] = capitalSport
        sub_sport = activity['sub_sport']
        display_sport = sport if sport in ('running', 'cycling', 'rowing') and sub_sport == 'generic' else sub_sport
        display_sport = f'{display_sport.title()}'.replace('_', ' ')
        #capitalize all first letters of each word in display_sport
        display_sport_capital = display_sport.title()
        activity_dict['DisplaySport'] = display_sport_capital
        total_time = time_seconds_to_string(activity['total_time'])
        activity_dict['Duration'] = total_time
        elapsed_time = time_seconds_to_string(activity['total_elapsed_time'])
        activity_dict['Elapsed Time'] = elapsed_time
        activity_dict['Avg HR'] = int(activity['avg_hr'])
        activity_dict['Max HR'] = int(activity['max_hr'])
        activity_dict['Recovery HR'] = int(activity['recovery_hr'])
        activity_dict['Resting Calories'] = int(activity['resting_calories'])
        activity_dict['Total Calories'] = int(activity['total_calories'])
        activity_dict['Active Calories'] = int(activity['total_calories'] - activity['resting_calories'])
        activity_dict['Sweat Loss'] = int(activity['sweat_loss'])
        total_descent = activity['total_descent']
        activity_dict['Total Descent'] = round(float(total_descent * 3.28084), 3)
        total_ascent = activity['total_ascent']
        activity_dict['Total Ascent'] = round(float(total_ascent * 3.28084), 3)
        if sport == 'running':
            activity_dict = prepare_running(activity, activity_dict)
        elif sport == 'cycling':
            activity_dict = prepare_cycling(activity, activity_dict)
        elif sport == 'rowing':
            activity_dict = prepare_rowing(activity, activity_dict)
        activity_list.append(activity_dict)
    return activity_list

def updateTitle(new_title, new_description, new_timestamp, activity_id):
    #check to see what is getting passed as new title, new description, new timestamp
    new_title = None if new_title == '' else new_title
    new_description = None if new_description == '' else new_description
    new_timestamp = None if new_timestamp == '' else new_timestamp
    print(f'TITLE: {new_title}')
    print(f'DECRIPTION: {new_description}')
    print(f'TIMESTAMP: {new_timestamp}')
    print(f'ACTIVITY ID: {activity_id}')
    cnxn = connect_to_postgres()
    cnxn.autocommit = True
    # call function edit title with above params
    cursor = cnxn.cursor()
    query = 'select public.edittitle(%s, %s, %s, %s)'
    cursor.execute(query, (activity_id, new_title, new_description, new_timestamp))
    # cursor.callproc('edittitle', (activity_id, new_title, new_description, new_timestamp))
    cursor.close()
    cnxn.close()
    return

## Route Helper Functions
def preMonthDetail(month, year):
    start_date = pd.Timestamp(f'{year}-{month}-01')
    end_date = pd.Timestamp(f'{year}-{month}-01') + pd.offsets.MonthEnd(0)
    session_df, lap_df = get_activity_info_by_date_range(start_date.date(), end_date.date())
    if len(session_df)==0:
        print("NO ACTIVITY FOUND")
        return render_template('searchByMonth.html')
    activity_list = prepare_multiple_activities(session_df)
    lap_html_list = prepare_lap_info(lap_df)
    ## activity list and lap html list are too large to store in session, so we store them in the database and store the id in the session
    activity_list_id = create_cookie(json.dumps(activity_list))
    session['activity_list'] = activity_list_id
    lap_html_list_id = create_cookie(json.dumps(lap_html_list))
    session['lap_html_list'] = lap_html_list_id
    month_string = pd.to_datetime(f'{month}/01/{year}').strftime('%B %Y')
    session['date_title'] = month_string
    session['source'] = 'searchByMonth'
    print("ACTIVITY FOUND")
    return redirect(url_for('multiple_activity'))

def preSingleDate(timestamp):
    session_df, lap_df = get_activity_info_by_date(timestamp.date())
    if len(session_df) == 0:
        print("NO ACTIVITY FOUND")
        return render_template('searchByDate.html')
    activity_list = prepare_multiple_activities(session_df)
    lap_html_list = prepare_lap_info(lap_df )
    date_string = timestamp.strftime('%B %d %Y')
    ## activity list and lap html list are too large to store in session, so we store them in the database and store the id in the session
    lap_html_list_id = create_cookie(json.dumps(lap_html_list))
    session['lap_html_list'] = lap_html_list_id
    activity_list_id = create_cookie(json.dumps(activity_list))
    session['activity_list'] = activity_list_id
    session['date_title'] = date_string
    session['source'] = 'searchByDate'
    # Redirect or render a template based on the processing result
    print("ACTIVITY FOUND")
    return redirect(url_for('multiple_activity'))

## Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_error = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        account_id = verify_user(username, password)

        if account_id is not None:
            # Redirect to home page
            print("LOGIN SUCCESSFUL")
            session['logged_in'] = True
            return redirect(url_for('homePage'))
        else:
            # Redirect to login with error message
            session['logged_in'] = False
            login_error = True
    
    return render_template('login.html', show_error=login_error)

@app.route('/registrationPage', methods=['GET', 'POST'])
def registerPage():
    if request.method == 'POST':
        # Access the form data:
        firstname = request.form['first-name']
        lastname = request.form['last-name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        register_user(firstname, lastname, username, password)
        send_registration_email(email, firstname, lastname)
        return redirect(url_for('login'))
    return render_template('registration.html')
    
@app.route('/searchByMonth', methods=['GET', 'POST'])
@login_required
def searchByMonth():
    if request.method == 'POST':
        # Access the form data:
        button_pressed = request.form['search']
        month = request.form['month']
        year = request.form['year']
        return preMonthDetail(month, year)
        # if button_pressed == 'summary':
        #     return pre_MonthSummary(month, year)
        # elif button_pressed == 'detail':
        #     return preMonthDetail(month, year)
        # else: # button_pressed == 'recap'
            # return pre_monthgroupweek(month, year)
    
    return render_template('searchByMonth.html')

@app.route('/searchByDate', methods=['GET', 'POST'])
@login_required
def searchByDate():
    if request.method == 'POST':
        # Access the form data:
        date_str = request.form['date']
        timestamp = pd.to_datetime(date_str)
        return preSingleDate(timestamp)
    
    return render_template('searchByDate.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register')
def register():
    # Render the registration page
    return render_template('registration.html')  # Ensure you have a registration.html template

@app.route('/homePage', methods=['GET', 'POST'])
@login_required
def homePage():
    return render_template('homePage.html')

@app.route('/multiple_activity')
@login_required
def multiple_activity():
    # Render the multiple_activity.html page
    lap_html_list_id = session['lap_html_list']
    lap_html_list = get_cookie_value(lap_html_list_id)
    activity_list_id = session['activity_list']
    activity_list = get_cookie_value(activity_list_id)
    return render_template('multipleActivity.html', activity_list=activity_list, date_title = session['date_title'], lap_html_list=lap_html_list, source=session['source'], zip=zip)

@app.route('/editTitle', methods=['GET', 'POST'])
@login_required
def editTitle():
    if request.method == 'POST':
        # Access the form data:
        new_title = request.form['title']
        # print(f'TITLE: {new_title}')
        new_description = request.form['description']
        # print(f'DESCRITION: {new_description}')
        new_date = request.form['date']
        new_time = request.form['time']
        new_timestamp = pd.to_datetime(f'{new_date} {new_time}')
        # print(f'TIMESTAMP: {new_timestamp}')
        activity_id = request.form['activity_id']
        source = request.form['source']
        old_date = pd.to_datetime(request.form['old_date'])
        updateTitle(new_title, new_description, new_timestamp, activity_id)
        if source == 'searchByDate':
            return preSingleDate(old_date)
        else:
            return preMonthDetail(old_date.month, old_date.year)
