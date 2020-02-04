from models.base_model import BaseModel
from models.user import User
import peewee as pw
from playhouse.hybrid import hybrid_property 

class Follow_Request(BaseModel):
    follow_requester = pw.ForeignKeyField(User, backref="follow_requestings") # Current logged in user is the follow requester
    follow_requested_user = pw.ForeignKeyField(User, backref="follow_requesters") # The logged in user will request to follow another user
    # user.follow_requestings will give all the users that the current logged in user has requested to follow
    # user.follow_requesters will give all the users that have requested to follow the current logged in user

    @hybrid_property
    def sfollow_requester_id(self):
        return self.follow_requested_user