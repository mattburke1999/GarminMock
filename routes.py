from flask import Blueprint, request
from views import show_register, register, login, check_login, home, homePage, show_login_form,\
    show_searchByDate_form, searchByDate, multiple_activity, show_searchByMonth_form, searchByMonth,\
    show_searchByYear_form, default, logout, activity


bp = Blueprint('main', __name__)


def login_required(f):
    return check_login(f)

@bp.route('/registrationPage')
def show_register_route():
    return show_register()

@bp.route('/register', methods=['POST'])
def register_route():
    return register()

@bp.route('/login', methods=['POST'])
def login_route():
    return login()

@bp.route('/login_form', methods=['GET'])
def show_login_form_route():
    return show_login_form()

@bp.route('/')
@login_required
def home_route():
    return homePage()

@bp.route('/homePage', methods=['GET'])
@login_required
def homePage_route():
    return homePage()

@bp.route('/searchByDate', methods=['GET'])
@login_required
def show_searchByDate_form_route():
    return show_searchByDate_form()

@bp.route('/ByDate', methods=['GET'])
@login_required
def searchByDate_route():
    date = request.args.get('date')
    return searchByDate(date)

@bp.route('/multiple_activity')
@login_required
def multiple_activity_route():
    return multiple_activity()

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