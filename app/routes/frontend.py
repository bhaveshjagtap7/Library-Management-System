from flask import Blueprint, render_template

frontend_blueprint = Blueprint('frontend', __name__)


@frontend_blueprint.route('/')
def index():
    return render_template('dashboard.html')


@frontend_blueprint.route('/books')
def books_page():
    return render_template('books.html')


@frontend_blueprint.route('/users')
def users_page():
    return render_template('users.html')


@frontend_blueprint.route('/loans')
def loans_page():
    return render_template('loans.html')
