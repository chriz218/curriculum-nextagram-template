# PAYMENT views 

from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for
from app import gateway
from models.user import User
from models.picture import Picture
from models.payment import Payment
from flask_login import current_user

# Blueprints are required to be registered in __init__.py
payment_blueprint = Blueprint('payment',
                            __name__,
                            template_folder='templates')     

                                           
@payment_blueprint.route("/<picture_id>/client_token", methods=["POST"])
def client_token(picture_id):
    picture = Picture.get_by_id(picture_id)
    client_token = gateway.client_token.generate()  
    return render_template('/payment/donate.html', client_token=client_token, picture=picture, picture_id=picture_id)

@payment_blueprint.route("/<picture_id>/checkout", methods=["POST"])
def create_purchase(picture_id):
    donation_amount = request.form.get('donation-amount')
    donation_message = request.form.get('donation-message')
    nonce = request.form.get('nonce')
    result = gateway.transaction.sale({
        "amount": donation_amount,
        "payment_method_nonce": nonce,
        "options": {
        "submit_for_settlement": True
        }
    })

    if result:
        new_payment_instance = Payment(donor_id=current_user.id, payment_amount=donation_amount, message=donation_message, picture_id=picture_id)
        new_payment_instance.save()
        picture = Picture.get_by_id(picture_id)
        user = User.get_by_id(picture.user_id)
        flash('Payment successful')
        return redirect(url_for('users.show', username=user.name))
    else:
        flash('Payment unsuccessful. Please try again.')
        return render_template('home.html')