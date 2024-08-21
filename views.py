from flask import render_template, redirect, url_for, session, request, jsonify, make_response
from config import FLASK_ENV
from services import register_process, login_process, single_date, month_detail, get_single_activity_info, get_calendar_info, get_home_page_posts, search_for_editing, merge_check_process
from functools import wraps
import ast

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

def homePage(sport=None):
    result = get_home_page_posts(0, 15, sport)
    if not result[0]:
        return show_error_page(result[1], 'get_home_page_posts', 'Error getting home page posts.')
    return mult_activity(None, result[1]['activity_list'], result[1]['lap_list'], result[1]['record_html_list'], enable_load_more=True)

def get_more_posts(offset, limit, sport):
    result = get_home_page_posts(offset, limit, sport, render=True)
    if not result[0]:
        return jsonify((False, 'No more posts found'))
    return jsonify((True, result[1]))

def searchPage():
    return render_template('searchPage.html')

def show_searchByDate_form():
    return render_template('searchByDate.html')

def searchByDate(date_str):
    result = single_date(date_str)
    if not result[0]:
        return show_error_page(result[1], 'single_date', 'Error getting activity information.')
    return mult_activity(None, result[1]['activity_list'], result[1]['lap_list'], result[1]['record_html_list'])

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
    if not result[0]:
        return show_error_page(result[1], 'month_detail', 'Error getting month information.')
    return mult_activity(result[1]['date_title'], result[1]['activity_list'], result[1]['lap_list'], result[1]['record_html_list'])

def mult_activity(date_title, activity_list, lap_html_list, folium_maps, enable_load_more=False):
    return render_template('multipleActivity.html', date_title=date_title, activity_list=activity_list, lap_html_list=lap_html_list, folium_maps=folium_maps, zip=zip, len=len, list=list, enable_load_more=enable_load_more)

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
    return display_activity(result[1]['activity_list'][0], result[1]['lap_list'][0], result[1]['record_html_list'][0])

def display_activity(activity, lap_html, folium_map):
    if type(activity) == str:
        activity = ast.literal_eval(activity)
    return render_template('singleActivity.html', activity=activity, lap_html=lap_html, folium_map=folium_map)
    
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

def show_edit_form():
    return render_template('editPage.html')

def search_activities_for_editing(input, input_type):
    result = search_for_editing(input, input_type)
    if not result[0]:
        print("FALSE")
        return make_response(jsonify({'error': result[1]}), 400)
    return make_response(jsonify({'success': result[1]}), 200)

def merge_check(activity1, activity2):
    result = merge_check_process(activity1, activity2)
    if result[0]:
        return make_response(jsonify({'data': result[1]}), 200)
    return make_response(jsonify({'error': result[1]}), 400)