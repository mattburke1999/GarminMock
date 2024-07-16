from flask import Blueprint, request, render_template
from views import register, login, check_login, searchByDate, searchByMonth, logout, activity, get_calendar, switch_month

bp = Blueprint('main', __name__)

def login_required(f):
    return check_login(f)

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
    data = request.get_json()
    username = data['username']
    password = data['password']
    return login(username, password)

@bp.route('/')
def home_route():
    return render_template('login.html')

@bp.route('/ByDate', methods=['GET'])
@login_required
def searchByDate_route():
    date = request.args.get('date')
    return searchByDate(date)

@bp.route('/ByMonth', methods=['GET'])
@login_required
def searchByMonth_route():
    month = request.args.get('month')
    year = request.args.get('year')
    return searchByMonth(month, year)

@bp.route('/logout', methods=['GET'])
def logout_route():
    return logout()

@bp.route('/activity/<activity_id>')
@login_required
def activity_route(activity_id):
    return activity(activity_id)

@bp.route('/calendar/', methods=['GET'])
@login_required
def calendar_route():
    return get_calendar()

@bp.route('/switch_month/<int:year>/<int:month>')
@login_required
def switch_month_route(year, month):
   return switch_month(year, month)