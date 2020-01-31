# PAYMENT views 

import os
from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for
from app import gateway
from models.user import User
from models.picture import Picture
from models.payment import Payment
from flask_login import current_user
from sendgrid import SendGridAPIClient # For sending emails
from sendgrid.helpers.mail import Mail # For sending emails

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

        message = Mail(
            from_email=current_user.email,
            to_emails=user.email,
            subject=f"Nextagram: New Donation from {current_user.name.capitalize()}",
            html_content=f"<p>Dear {user.name.capitalize()},</p><br><p>{current_user.name.capitalize()} has just donated ${donation_amount} to you!</p><br><p>{current_user.name.capitalize()}\'s message: {donation_message}</p><br><p>With love,</p><br><p>Nextagram</p>")
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            flash('Payment successful')
        except Exception as e:
            print(str(e))
        return redirect(url_for('users.show', username=user.name))
    else:
        flash('Payment unsuccessful. Please try again.')
        return render_template('home.html')