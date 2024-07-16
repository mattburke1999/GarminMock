from flask import redirect, url_for, session, jsonify
from config import FLASK_ENV
from services import register_process, login_process, single_date, month_detail, get_single_activity_info, get_calendar_info
from functools import wraps

def register(firstname, lastname, email, username, password):
    result = register_process(firstname, lastname, email, username, password)
    return jsonify(result[1], 200) if result[0] else jsonify(result[1], 400)

def login(username, password):
    result = login_process(username, password)
    return jsonify(result[1], 200) if result[0] else jsonify(result[1], 400)

def searchByDate(date_str):
    result = single_date(date_str)
    return jsonify(result[1], 200) if result[0] else jsonify(result[1], 400)
    
def searchByMonth(month, year):
    result = month_detail(month, year)
    return jsonify(result[1], 200) if result[0] else jsonify(result[1], 400)

def logout():
    session['logged_in'] = False
    return redirect(url_for('main.show_login_form_route'))

def activity(activity_id):
    result = get_single_activity_info(activity_id)
    return jsonify(result[1], 200) if result[0] else jsonify(result[1], 400)

def get_calendar():
    result = get_calendar_info()
    if not result[0]:
        return jsonify(result[1], 400)
    cal, month_string, month, year, current_month = result[1]    
    return jsonify({'calendar': cal, 'calendar_title': month_string, 'month': month, 'year': year, 'current_month': current_month}, 200)

def switch_month(year, month):
    session['month'] = month
    session['year'] = year
    return redirect(url_for('main.calendar_route'))

def check_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session['logged_in'] == False:
            print("NOT LOGGED IN")
            return jsonify('You are not logged in', 401)
        return f(*args, **kwargs)
    return decorated_function