import os # To call things from .env
import config
from flask import Flask
from models.base_model import db
from flask_login import LoginManager # To handle login
from models.user import User
import braintree # This is to handle payment (The card information section)
from authlib.flask.client import OAuth # Google


web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')

app = Flask('NEXTAGRAM', root_path=web_dir)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

login_manager = LoginManager() # To handle login
login_manager.init_app(app)

# Payment
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id = os.environ.get("merchant_id"), # Put the keys in .env
        public_key = os.environ.get("public_key"), # Put the keys in .env
        private_key = os.environ.get("private_key") # Put the keys in .env
    )
)

# Google
oauth = OAuth()

oauth.register('google',
    client_id = os.environ.get("GOOGLE_CLIENT_ID"),  
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={
        'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'token_endpoint_auth_method': 'client_secret_basic',
        'token_placement': 'header',
        'prompt': 'consent'
    }
)


@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        print(db)
        print(db.close())
    return exc

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id) # To handle login
