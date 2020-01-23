## Views for Users (for sign up, for example)
from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash # This function allows one to hash a password
from models.user import User

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

# user profile page
@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass

# a page to list out all users
@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"

# user profile edit page
@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass

# form action for profile edit
@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass

# Sign Up Page (new)
@users_blueprint.route("/signup")
def sign_up():
   return render_template('users/signup.html')  

# Sign Up (Create)
@users_blueprint.route("/", methods=["POST"])
def signup_form():
   username = request.form.get('username') # Get from the input named, username, from the form in signup.html
   email = request.form.get('email') # Get from the input named, email, from the form in signup.html
   password = request.form.get('password') # Get from the input named, password, from the form in signup.html
   confirm_password = request.form.get('password-confirm') # Get from the input named, password-confirm, from the form in signup.html

   if password != confirm_password:
       flash("Passwords do not match")
       return render_template('users/signup.html')
   
   new_user_instance = User(name=username.lower(), email=email.lower(), password=password) # Create an instance (row) for Users
   if new_user_instance.save():
      flash(f"Sign up successful! Your username is {username}.")
      return redirect(url_for('users.sign_up'))
   else:    
      for i in new_user_instance.errors:
          flash(i)     
      return render_template('users/signup.html',errors=new_user_instance.errors)   