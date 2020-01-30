from models.base_model import BaseModel
from models.user import User
from models.picture import Picture
import peewee as pw
     
class Payment(BaseModel): 
    donor = pw.ForeignKeyField(User, backref="payments") # A donor can have multiple payments
    payment_amount = pw.DecimalField(decimal_places=2)
    picture = pw.ForeignKeyField(Picture, backref="payments") # A picture can have a number of payments
    message = pw.CharField()