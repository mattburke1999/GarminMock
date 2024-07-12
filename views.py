from flask import render_template, redirect, url_for, session, request
from config import FLASK_ENV
from services import register_process, login_process, single_date, month_detail, get_multiple_activity_info, get_single_activity_info, get_calendar_info
from functools import wraps

def show_register():
    return render_template('registration.html')

def register(firstname, lastname, email, username, password):
    result = register_process(firstname, lastname, email, username, password)
    return redirect(url_for('login')) if result[0] else render_template('registration.html', error=result[1])

def login(username, password):
    result = login_process(username, password)
    return redirect(url_for('main.homePage_route')) if result[0] else render_template('login.html', show_error=result[1])

def show_login_form(login_error):
    return render_template('login.html', show_error=login_error)

def home():
    return redirect(url_for('main.show_login_form_route'))

def homePage():
    return render_template('homePage.html')

def show_searchByDate_form():
    return render_template('searchByDate.html')

def searchByDate(date_str):
    result = single_date(date_str)
    return redirect(url_for('main.multiple_activity_route')) if result[0] else render_template('searchByDate.html', error=result[1])

def show_searchByMonth_form():
    return render_template('searchByMonth.html')

def show_error_page(error, service_method, prod_error):
    if FLASK_ENV == 'production':
        service_method = None
        error = prod_error
        prod_error = None
    return render_template('error.html', error_message=error, service_method=service_method, prod_error=prod_error)
    
def searchByMonth(month, year):
    result = month_detail(month, year)
    return redirect(url_for('main.multiple_activity_route')) if result[0] else render_template('searchByMonth.html', error=result[1])

def multiple_activity():
    result = get_multiple_activity_info()
    if not result[0]:
        return show_error_page(result[1], 'get_multiple_activity_info', 'Error getting activity information.')
    activity_list, lap_html_list, folium_maps = result[1]
    return render_template('multipleActivity.html', activity_list=activity_list, date_title = session['date_title'], lap_html_list=lap_html_list, folium_maps = folium_maps, zip=zip)

def show_searchByYear_form():
    return render_template('searchByYear.html')

def default():
    return render_template('base.html')

def logout():
    session['logged_in'] = False
    return redirect(url_for('main.show_login_form_route'))

def activity(activity_id):
    result = get_single_activity_info(activity_id)
    if not result[0]:
        return show_error_page(result[1], 'get_single_activity_info', 'Error getting activity information.')
    activity_dict, lap_html, folium_map = result[1]
    return render_template('singleActivity.html', activity=activity_dict, lap_html=lap_html, folium_map=folium_map)

def get_calendar():
    result = get_calendar_info()
    if not result[0]:
        return show_error_page(result[1], 'get_calendar_info', 'Error getting calendar information.')
    cal, month_string, month, year, current_month = result[1]    
    return render_template('calendar.html', calendar=cal, calendar_title=month_string, month=month, year=year, current_month=current_month, sport='Other', zip=zip)

def switch_month(year, month):
    session['month'] = month
    session['year'] = year
    return redirect(url_for('main.calendar_route'))

def check_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session['logged_in'] == False:
            print("NOT LOGGED IN")
            return redirect(url_for('main.show_login_form_route', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
