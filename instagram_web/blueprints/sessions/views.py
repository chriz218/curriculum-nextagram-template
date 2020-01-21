# SESSIONS views (for Login and Logout)

from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for
from models.user import User

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

# this blueprint has no url prefix

@sessions_blueprint.route('/login')
def new():
    # email = request.form.get('email')
    # user = User.get_or_none(User.email == email)
    # user = User.select().where(User.email.iregexp(email)).get()
    # result = check_password_hash(hashed_password, password_to_check)
    # if result:
    #     login_user(user)
    return render_template('sessions/login.html') 

@sessions_blueprint.route('/sessions', methods=["POST"])
def create():
   username = request.form.get('username') # Get from the input named, username, from the form in signup.html
   password = request.form.get('password') # Get from the input named, password, from the form in signup.html

@sessions_blueprint.route('/logout', methods=["POST"])
def destroy():
    pass