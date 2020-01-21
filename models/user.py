from models.base_model import BaseModel
import peewee as pw
import re
     
class User(BaseModel): # User is a class that inherits from another class called BaseModel
    name = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = pw.CharField(unique=False)

    def validate(self):
        duplicate_username = User.get_or_none(User.name == self.name)
        duplicate_email = User.get_or_none(User.email == self.email)
        email_format = '[A-Za-z0-9]+@+[a-z]+[.]+.[A-Za-z\.]+'
        # password_format = '[A-Za-z0-9@#$%^&+=]{8,}'   ## TO BE ADDED EVENTUALLY

        if duplicate_username:
            self.errors.append('Usersame already exists')

        if duplicate_email:
            self.errors.append('Email address already in use')

        if re.search(email_format, self.email) is None:
            self.errors.append('Invalid email address')    

        if len(self.password) < 8:
            self.errors.append('Password needs to have at least 8 characters')   





 

         



