from flask import Blueprint, request
from views import show_register, register, login, check_login, home, homePage, show_login_form,\
    show_searchByDate_form, searchByDate, show_searchByMonth_form, searchByMonth,display_activity,\
    show_searchByYear_form, default, logout, activity, get_calendar, switch_month, searchPage, get_more_posts


bp = Blueprint('main', __name__)

def login_required(f):
    return check_login(f)

@bp.route('/registrationPage')
def show_register_route():
    return show_register()

@bp.route('/register', methods=['POST'])
def register_route():
    firstname = request.form['first-name']
    lastname = request.form['last-name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    return register(firstname, lastname, email, username, password)

@bp.route('/login', methods=['POST'])
def login_route():
    username = request.form['username']
    password = request.form['password']
    return login(username, password)

@bp.route('/login_form', methods=['GET'])
def show_login_form_route():
    login_error = request.args.get('show_error')
    print(f'LOGIN ERROR: {login_error}')
    return show_login_form(login_error)

@bp.route('/', methods=['GET'])
@login_required
def homePage_route():
    return homePage()

@bp.route('/filter_posts', methods=['GET'])
@login_required
def filter_posts_route():
    sport = request.args.get('sport')
    return get_more_posts(0, 15, sport)

@bp.route('/load_more', methods=['GET'])
@login_required
def load_more_route():
    offset = request.args.get('offset')
    sport = request.args.get('sport')
    return get_more_posts(offset, 10, sport)

@bp.route('/searchPage', methods=['GET'])
@login_required
def searchPage_route():
    return searchPage()

@bp.route('/searchByDate', methods=['GET'])
@login_required
def show_searchByDate_form_route():
    return show_searchByDate_form()

@bp.route('/multiple_activity', methods=['GET'])
@login_required
def searchByDate_route():
    date = request.args.get('date1')
    date2 = request.args.get('date2')
    print(f'DATE1: {date}, DATE2: {date2}')
    if date2: 
        return searchByMonth(date, date2)#(month and year)
    return searchByDate(date)#(single date)

@bp.route('/searchByMonth', methods=['GET'])
@login_required
def show_searchByMonth_form_route():
    return show_searchByMonth_form()

@bp.route('/ByMonth', methods=['GET'])
@login_required
def searchByMonth_route():
    month = request.args.get('month')
    year = request.args.get('year')
    return searchByMonth(month, year)

@bp.route('/searchByYear_form', methods=['GET'])
@login_required
def show_searchByYear_form_route():
    return show_searchByYear_form()

@bp.route('/default', methods=['GET'])
@login_required
def default_route():
    return default()

@bp.route('/logout', methods=['GET'])
def logout_route():
    return logout()

@bp.route('/activity/<activity_id>')
@login_required
def activity_route(activity_id):
    return activity(activity_id)

@bp.route('/activity', methods=['POST'])
def activity_route_post():
    activity = request.form.get('activity')
    lap_html = request.form.get('lap_html')
    folium_map = request.form.get('folium_map')
    return display_activity(activity, lap_html, folium_map)

@bp.route('/calendar', methods=['GET'])
@login_required
def calendar_route():
    return get_calendar()

@bp.route('/switch_month/<int:year>/<int:month>')
@login_required
def switch_month_route(year, month):
   return switch_month(year, month)