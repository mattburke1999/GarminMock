from flask import Blueprint
from views import show_register, register, login, check_login, home, homePage, show_login_form,\
    show_searchByDate_form, searchByDate, multiple_activity, show_searchByMonth_form, searchByMonth,\
    editTitle, show_searchByYear_form


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
def home_route():
    return home()

@bp.route('/homePage', methods=['GET'])
@login_required
def homePage_route():
    return homePage()

@bp.route('/searchByDate_form', methods=['GET'])
@login_required
def show_searchByDate_form_route():
    return show_searchByDate_form()

@bp.route('/searchByDate', methods=['POST'])
@login_required
def searchByDate_route():
    return searchByDate()

@bp.route('/multiple_activity')
@login_required
def multiple_activity_route():
    return multiple_activity()

@bp.route('/searchByMonth_form', methods=['GET'])
@login_required
def show_searchByMonth_form_route():
    return show_searchByMonth_form()

@bp.route('/searchByMonth', methods=['POST'])
@login_required
def searchByMonth_route():
    return searchByMonth()

@bp.route('/searchByYear_form', methods=['GET'])
@login_required
def show_searchByYear_form_route():
    return show_searchByYear_form()

@bp.route('editTitle', methods=['POST'])
@login_required
def editTitle_route():
    return editTitle()