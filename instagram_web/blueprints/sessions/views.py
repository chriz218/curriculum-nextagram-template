# SESSIONS views (for Login and Logout)

from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for
from models.user import User
from werkzeug.security import check_password_hash
from models.user import User
from flask_login import login_user, current_user, login_required, logout_user

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')                            

# this blueprint has no url prefix

@sessions_blueprint.route('/login')
def new():
    return render_template('sessions/login.html') 

# User will not see this URL
@sessions_blueprint.route('/sessions', methods=["POST"])
def create():
   username = request.form.get('username').lower() # Get from the input named, username, from the form in login.html
   password_to_check = request.form.get('password') # Get from the input named, password, from the form in login.html
   user = User.get_or_none(User.name == username) # user is a row in User; select the row where user.name matches username\

   if user is None:  
       flash(f"Invalid username or password.")    
       return render_template('/sessions/login.html') 

   hashed_password = user.password
   result = check_password_hash(hashed_password, password_to_check)

   if result == True:
       flash(f"Login successful.")
       login_user(user)
       return redirect(url_for('home'))
   else:
       flash(f"Invalid username or password.")    
       return render_template('/sessions/login.html') 


@sessions_blueprint.route('/logout', methods=["POST"])
@login_required
def destroy():
    logout_user()
    flash(f"Logout successful.")
    return redirect(url_for('home'))