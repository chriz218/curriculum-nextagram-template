from models.base_model import BaseModel
from models.user import User
import peewee as pw
import re
from config import S3_LOCATION
from playhouse.hybrid import hybrid_property # To get the url of uploaded pictures
     
class Picture(BaseModel): 
    picture_name = pw.CharField()
    user = pw.ForeignKeyField(User, backref="pictures") # A user can have multiple pictures

    def get_total_amount(self):
        #self.payments => [payment#1, payment#4, payment#5]
        #              => [30, 40, 100]
        # payments backref
        return sum([e.payment_amount for e in self.payments])

    # To get the url of uploaded pictures
    @hybrid_property
    def picture_url(self):
        return S3_LOCATION + self.picture_name