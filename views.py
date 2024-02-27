from flask import render_template, request, redirect, url_for, session
from dataAccess import DataAccess
from dataTransform import DataTransform
import os
import smtplib
from functools import wraps
import pandas as pd
import json

da = DataAccess()
dt = DataTransform()

def show_register():
    return render_template('registration.html')

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

def register():
    firstname = request.form['first-name']
    lastname = request.form['last-name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    da.register_user(firstname, lastname, username, password)
    send_registration_email(email, firstname, lastname)
    return redirect(url_for('login'))

def check_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session['logged_in'] == False:
            print("NOT LOGGED IN")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def login():
    login_error = False
    username = request.form['username']
    password = request.form['password']
    
    account_id = da.verify_user(username, password)

    if account_id is not None:
        # Redirect to home page
        print("LOGIN SUCCESSFUL")
        session['logged_in'] = True
        return redirect(url_for('main.homePage_route'))
    else:
        # Redirect to login with error message
        session['logged_in'] = False
        login_error = True
        return redirect(url_for('main.show_login_form_route', show_error=login_error))

def show_login_form():
    login_error = request.args.get('show_error')
    return render_template('login.html', show_error=login_error)

def home():
    return redirect(url_for('main.show_login_form_route'))

def homePage():
    return render_template('homePage.html')

def show_searchByDate_form():
    return render_template('searchByDate.html')

def preSingleDate(timestamp):
    session_df, lap_df = da.get_activity_info_by_date(timestamp.date())
    if len(session_df) == 0:
        print("NO ACTIVITY FOUND")
        return render_template('searchByDate.html')
    activity_list = dt.prepare_multiple_activities(session_df)
    lap_html_list = dt.prepare_lap_info(lap_df, session_df)
    date_string = timestamp.strftime('%B %d %Y')
    ## activity list and lap html list are too large to store in session, so we store them in the database and store the id in the session
    lap_html_list_id = da.create_cookie(json.dumps(lap_html_list))
    session['lap_html_list'] = lap_html_list_id
    activity_list_id = da.create_cookie(json.dumps(activity_list))
    session['activity_list'] = activity_list_id
    session['date_title'] = date_string
    session['source'] = 'searchByDate'
    # Redirect or render a template based on the processing result
    print("ACTIVITY FOUND")
    return redirect(url_for('main.multiple_activity_route'))

def searchByDate():
    date_str = request.form['date']
    timestamp = pd.to_datetime(date_str)
    return preSingleDate(timestamp)

def show_searchByMonth_form():
    return render_template('searchByMonth.html')

def preMonthDetail(month, year):
    start_date = pd.Timestamp(f'{year}-{month}-01')
    end_date = pd.Timestamp(f'{year}-{month}-01') + pd.offsets.MonthEnd(0)
    session_df, lap_df = da.get_activity_info_by_date_range(start_date.date(), end_date.date())
    if len(session_df)==0:
        print("NO ACTIVITY FOUND")
        return render_template('searchByMonth.html')
    activity_list = dt.prepare_multiple_activities(session_df)
    lap_html_list = dt.prepare_lap_info(lap_df, session_df)
    ## activity list and lap html list are too large to store in session, so we store them in the database and store the id in the session
    activity_list_id = da.create_cookie(json.dumps(activity_list))
    session['activity_list'] = activity_list_id
    lap_html_list_id = da.create_cookie(json.dumps(lap_html_list))
    session['lap_html_list'] = lap_html_list_id
    month_string = pd.to_datetime(f'{month}/01/{year}').strftime('%B %Y')
    session['date_title'] = month_string
    session['source'] = 'searchByMonth'
    print("ACTIVITY FOUND")
    return redirect(url_for('main.multiple_activity_route'))

def searchByMonth():
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

def multiple_activity():
    lap_html_list_id = session['lap_html_list']
    lap_html_list = da.get_cookie_value(lap_html_list_id)
    activity_list_id = session['activity_list']
    activity_list = da.get_cookie_value(activity_list_id)
    return render_template('multipleActivity.html', activity_list=activity_list, date_title = session['date_title'], lap_html_list=lap_html_list, source=session['source'], zip=zip)

def show_searchByYear_form():
    return render_template('searchByYear.html')

def editTitle():
    new_title = request.form['title']
    new_description = request.form['description']
    new_date = request.form['date']
    new_time = request.form['time']
    new_timestamp = pd.to_datetime(f'{new_date} {new_time}')
    activity_id = request.form['activity_id']
    source = request.form['source']
    old_date = pd.to_datetime(request.form['old_date'])
    da.updateTitle(new_title, new_description, new_timestamp, activity_id)
    if source == 'searchByDate':
        return preSingleDate(old_date)
    else:
        return preMonthDetail(old_date.month, old_date.year)

