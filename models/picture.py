from models.base_model import BaseModel
from models.user import User
import peewee as pw
import re
from config import S3_LOCATION
from playhouse.hybrid import hybrid_property # To get the url of uploaded pictures
     
class Picture(BaseModel): 
    picture_name = pw.CharField()
    user = pw.ForeignKeyField(User, backref="pictures")

    # To get the url of uploaded pictures
    @hybrid_property
    def picture_url(self):
        return S3_LOCATION + self.picture_name