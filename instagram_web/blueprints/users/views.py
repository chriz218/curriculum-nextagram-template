## Views for Users (for sign up, for example)
from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash # This function allows one to hash a password
from models.user import User
from models.picture import Picture
from flask_login import current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from instagram_web.util.helpers import *
from config import S3_KEY, S3_SECRET, S3_BUCKET, S3_LOCATION
from models.follow import Follow
from models.follow_request import Follow_Request

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

# user profile page
@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    user = User.get_or_none(name = username)
    if current_user.is_authenticated:
        if user is not None:
            # followers = user.followers            
            follower = Follow.get_or_none(follower_id = current_user.id, followed_user_id = user.id) 
            follow_requester = Follow_Request.get_or_none(follow_requester_id = current_user.id, follow_requested_user_id = user.id)
            images = user.pictures # Utilizing the backref
            number_of_followers = len(user.followers)
            number_of_followings = len(user.followings)
            return render_template('users/profile.html', user=user, images=images, follower=follower, follow_requester=follow_requester, number_of_followers=number_of_followers, number_of_followings=number_of_followings)
        else: 
            flash("This user does not exist")
            return redirect(url_for('home'))   
    else:
        flash('Please sign in to view profiles')
        return redirect(url_for('home'))    

# Navbar search box
@users_blueprint.route('/search', methods=["GET"])
def search():
    user_search = request.args.get('user-search').lower()
    return redirect(url_for('users.show', username=user_search))

# a page to list out all users
@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"

# user profile edit page
@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    return render_template('users/profileedit.html')

# form action for profile edit
@users_blueprint.route('/<id>/editprofile', methods=['POST'])####
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

##################
   if password != confirm_password:
       flash("Passwords do not match")
       return render_template('users/signup.html')
##################
#        
#    new_user_instance = User(name=username, email=email, password=password, confirm_password=confirm_password) # Create an instance (row) for Users
   new_user_instance = User(name=username, email=email, password=password) # Create an instance (row) for Users
   if new_user_instance.save():
      flash(f"Sign up successful! Your username is {username}.")
      return redirect(url_for('users.sign_up'))
   else:    
      for i in new_user_instance.errors:
          flash(i)     
      return render_template('users/signup.html',errors=new_user_instance.errors)  

## Profile Photo
@users_blueprint.route("/<username>/upload_profile_photo", methods=["POST"])
def upload_profile_photo(username):
    user = User.get_or_none(name = username)
    return render_template('users/uploadprofilepic.html', user=user)

@users_blueprint.route("/<username>/upload_profile_photo_file", methods=["POST"])
def upload_profile_photo_file(username):    
	# A
    if "user_profile_photo_file" not in request.files:
        return "No user_file key in request.files"

	# B
    file = request.files["user_profile_photo_file"]

	# C.
    if file.filename == "":
        return "Please select a file"

	# D.
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file, S3_BUCKET)
        query = User.update(profile_image = str(output)).where(User.id == current_user.id)
        if query.execute():
            return redirect(url_for('users.show', username=current_user.name))
        else:
            return redirect(url_for('users.upload_profile_photo'))      

    else:
        return redirect(url_for('users.upload_profile_photo'))     

## Photos
@users_blueprint.route("/<username>/upload", methods=["POST"])
def upload(username):
    user = User.get_or_none(name = username)
    return render_template('users/upload.html', user=user)

@users_blueprint.route("/<username>/upload_file", methods=["POST"])
def upload_file(username):    
	# A
    if "user_file" not in request.files:
        return "No user_file key in request.files"

	# B
    file = request.files["user_file"]

	# C.
    if file.filename == "":
        return "Please select a file"

	# D.
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file, S3_BUCKET)
        picture = Picture(picture_name=str(output),user=current_user.id)
        if picture.save():
            flash('Photo successfully uploaded')
            return redirect(url_for('users.show', username=current_user.name))
        else:
            return redirect(url_for('users.upload_file'))    

    else:
        return redirect(url_for('users.upload'))      

# Follow
@users_blueprint.route("/<id>/follow", methods=["POST"])
def follow(id):
    user = User.get_by_id(id)
    # new_follow_instance = Follow(follower_id=current_user.id, followed_user_id=user.id) # Need to swap
    new_follow_instance = Follow(follower_id=user.id, followed_user_id=current_user.id) # Need to swap
    if new_follow_instance.save():
        flash("Follow request accepted successfully")
        return redirect(url_for('users.follow_request', username=current_user.name), code=307) 
    else:
        flash("Something went wrong")
        return redirect(url_for('users.follow_request', username=current_user.name), code=307) 

# Unfollow
@users_blueprint.route("/<id>/unfollow", methods=["POST"])
def unfollow(id):
    user = User.get_by_id(id)
    unfollow = Follow.get_or_none(follower_id = current_user.id, followed_user_id = user.id) 
    if unfollow.delete_instance():
        flash("Unfollowed successfully")
        return redirect(url_for('users.show', username=user.name))
    else:
        flash("Something went wrong")
        return redirect(url_for('users.show', username=user.name))  


# Follow Request Page #
@users_blueprint.route("/<username>/follow_request", methods=["POST"])
def follow_request(username):
    follow_request_list = current_user.follow_requesters
    # follow_request_list = Follow_Request.get_or_none(follow_requested_user_id=current_user.id)
    return render_template('users/followrequest.html', follow_request_list=follow_request_list, User=User)

# Follow Request (Click on Follow button to request to follow)
@users_blueprint.route("/<id>/follow_request_send", methods=["POST"])
def follow_request_send(id):
    user = User.get_by_id(id)
    new_follow_request_instance = Follow_Request(follow_requester_id = current_user.id, follow_requested_user_id = user.id)
    if new_follow_request_instance.save():
        flash("Follow request submitted successfully")
        return redirect(url_for('users.show', username=user.name))
    else:
        flash("Something went wrong")
        return redirect(url_for('users.show', username=user.name))  

# Follow Request Accept (Click on Accept button to accept follow request)
@users_blueprint.route("/<id>/follow_request_accept", methods=["POST"])
def follow_request_accept(id):
    user = User.get_by_id(id)
    # follow_accept = Follow_Request.get_or_none(follow_requester_id = current_user.id, follow_requested_user_id = user.id) # Need to swap
    follow_accept = Follow_Request.get_or_none(follow_requester_id = user.id, follow_requested_user_id = current_user.id) # Need to swap
    if follow_accept.delete_instance():
        return redirect(url_for('users.follow', id=user.id), code=307)
        # return redirect(url_for('users.follow', id=current_user.id)) #########
    else:
        flash("Something went wrong")
        return redirect(url_for('users.follow_request', username=current_user.name), code=307)    

# Follow Request Delete (Click on Delete button to delete follow request)
@users_blueprint.route("/<id>/follow_request_delete", methods=["POST"])
def follow_request_delete(id):
    user = User.get_by_id(id)
    # follow_delete = Follow_Request.get_or_none(follow_requester_id = current_user.id, follow_requested_user_id = user.id) # Need to swap
    follow_delete = Follow_Request.get_or_none(follow_requester_id = user.id, follow_requested_user_id = current_user.id) # Need to swap
    if follow_delete.delete_instance():
        flash("Follow request deleted successfully")
        return redirect(url_for('users.follow_request', username=current_user.name), code=307)
    else: 
        flash("Something went wrong")
        return redirect(url_for('users.follow_request', username=current_user.name), code=307)

# Follow Request Cancel (Click on Cancel button to cancel follow request)
@users_blueprint.route("/<id>/follow_request_cancel", methods=["POST"])
def follow_request_cancel(id):
    user = User.get_by_id(id)
    follow_cancel = Follow_Request.get_or_none(follow_requester_id = current_user.id, follow_requested_user_id = user.id)
    if follow_cancel.delete_instance():
        flash("Follow request cancelled successfully")
        return redirect(url_for('users.show', username=user.name))
    else: 
        flash("Something went wrong")
        return redirect(url_for('users.show', username=user.name))  

# Following Page #
@users_blueprint.route("/<username>/following", methods=["POST"])
def following(username):
    user = User.get_or_none(name = username)
    following_list = user.followings
    return render_template('users/following.html', following_list=following_list, User=User, user=user)

# Follower Page #
@users_blueprint.route("/<username>/follower", methods=["POST"])
def follower(username):
    user = User.get_or_none(name = username)
    follower_list = user.followers
    return render_template('users/follower.html', follower_list=follower_list, User=User, user=user)    

# Privacy
@users_blueprint.route("/<id>/private", methods=["POST"])
def private(id):
    user = User.get_by_id(id)
    make_private = User.update(privacy = True).where(User.id == current_user.id)
    if make_private.execute():
        flash("Profile is now private")
        return redirect(url_for('users.show', username=user.name))
    else: 
        flash("Something went wrong")
        return redirect(url_for('users.show', username=user.name)) 

@users_blueprint.route("/<id>/public", methods=["POST"])
def public(id):
    user = User.get_by_id(id)    
    make_public = User.update(privacy = False).where(User.id == current_user.id)
    if make_public.execute():
        flash("Profile is now public")
        return redirect(url_for('users.show', username=user.name))
    else: 
        flash("Something went wrong")
        return redirect(url_for('users.show', username=user.name)) 