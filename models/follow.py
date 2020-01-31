from models.base_model import BaseModel
from models.user import User
import peewee as pw

class Follow(BaseModel):
    follower = pw.ForeignKeyField(User, backref="followings") # Current logged in user is the follower
    followed_user = pw.ForeignKeyField(User, backref="followers") # The logged in user will follow another user
    # user.followings will give all the users that the user is following
    # user.followers will give all the followers of a user