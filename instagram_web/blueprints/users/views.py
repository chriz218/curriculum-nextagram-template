## Views for Users (for sign up, for example)
from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash # This function allows one to hash a password
from models.user import User
from flask_login import current_user
from werkzeug.security import check_password_hash

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

# user profile page
@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    return render_template('users/profile.html')

# a page to list out all users
@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"

# user profile edit page
@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    return render_template('users/profileedit.html')

# form action for profile edit
@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    user = User.get_by_id(id)
    new_username = request.form.get('new-username').lower()
    new_email = request.form.get('new-email').lower()
    old_password = request.form.get('old-password')
    old_password_confirm = request.form.get('old-password-confirm')
    new_password = request.form.get('new-password')
    new_password_confirm = request.form.get('new-password-confirm')

    dict = {}

    if old_password != "":
        hashed_password = user.password
        result = check_password_hash(hashed_password, old_password) ## old_password will be hashed automatically
    
    if current_user.is_authenticated:
        if new_username != "":
            dict['name'] = new_username

        if new_email != "":
            dict['email'] = new_email

        if old_password != old_password_confirm:
            flash("Old passwords do not match")
            return render_template('users/profileedit.html')

        if new_password != new_password_confirm:
            flash("New passwords do not match")
            return render_template('users/profileedit.html')

        if old_password != "":
            if result == False:
                flash("Old password is wrong")   
                return render_template('users/profileedit.html') 

            if result == True and new_password == new_password_confirm and old_password == old_password_confirm and old_password != "" and new_password != "":
                dict['password'] = new_password
        
        user = User(id=id, **dict) ## **dict means unpacking the dictionary

        if user.save():
            flash("Successfully updated.")
            return redirect(url_for('users.edit', id=current_user.id))    
        else:
            for i in user.errors:
                flash(i)     
            return render_template('users/profileedit.html',errors=user.errors)  

    else:  
        flash("User not logged in")
        return render_template('sessions/login.html')  

# Sign Up Page (new)
@users_blueprint.route("/signup")
def sign_up():
   return render_template('users/signup.html')  

# Sign Up (Create)
@users_blueprint.route("/", methods=["POST"])
def signup_form():
   username = request.form.get('username').lower() # Get from the input named, username, from the form in signup.html
   email = request.form.get('email').lower() # Get from the input named, email, from the form in signup.html
   password = request.form.get('password') # Get from the input named, password, from the form in signup.html
   confirm_password = request.form.get('password-confirm') # Get from the input named, password-confirm, from the form in signup.html

#    if password != confirm_password:
#        flash("Passwords do not match")
#        return render_template('users/signup.html')
   
   new_user_instance = User(name=username, email=email, password=password, confirm_password=confirm_password) # Create an instance (row) for Users
   if new_user_instance.save():
      flash(f"Sign up successful! Your username is {username}.")
      return redirect(url_for('users.sign_up'))
   else:    
      for i in new_user_instance.errors:
          flash(i)     
      return render_template('users/signup.html',errors=new_user_instance.errors)   