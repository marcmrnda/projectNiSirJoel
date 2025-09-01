from flask import render_template,Blueprint,request,redirect,flash,url_for,session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .model.user import User
from . import db
from flask_cors import CORS
import os
import re
import smtplib
from dotenv import load_dotenv
import secrets
import string
from datetime import datetime

def generate_crypto_token(length=8):
    alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))



auth = Blueprint('auth',__name__)


CORS(auth, resources={r"/*": {"origins": "*"}})


@auth.route('/register', methods=["POST","GET"])
def register():
    if request.method == "POST":
            firstName = request.form.get('firstName')
            middleName = request.form.get('middleName')
            lastName = request.form.get('lastName')
            dateOfBirth = request.form.get('dateOfBirth')
            emailAddress = request.form.get('emailAddress')
            
            birth_date = datetime.strptime(dateOfBirth, "%m/%d/%Y").date()
            
            emailChecker = User.query.filter_by(emailAddress=emailAddress).first()
            
            if emailChecker:
                flash("Email Address already taken", category="error")
            else:
                # Example usage
                passwordGeneration = generate_crypto_token()
                new_user = User(firstName=firstName, middleName=middleName, lastName=lastName, dateOfBirth=birth_date, emailAddress=emailAddress, password=generate_password_hash(passwordGeneration,method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                 
                load_dotenv()  
                email_password = os.getenv('EMAIL_PASSWORD')
                email_user = os.getenv('EMAIL_USER')
                # creates SMTP session
                s = smtplib.SMTP('smtp.gmail.com', 587)
                # start TLS for security
                s.starttls()
                # Authentication
                s.login(email_user, email_password)
                # message to be sent
                passChecker = User.query.filter_by(emailAddress=emailAddress).first()
                message = f"Subject: Your Account Password\n\nYour account has been created successfully. Your password is: {passChecker.password}\nPlease change your password after logging in."
                # sending the mail
                s.sendmail(email_user, emailAddress, message)
                # terminating the session
                s.quit()

                flash("Account Created your password is sent on your email address", category="success")
                return jsonify({"message":"Account Created your password is sent on your email address"}), 201
                
    return jsonify({"message":"Account Created your password is sent on your email address"}), 201
    

@auth.route('/login', methods=["POST","GET"])
def login():
    if "emailAddress" in session and session["accountType"] == "User":
            flash("Login Successfully" , category="success")
            pass

    if "emailAddress" in session and session["accountType"] == "Admin":
            flash("Login Successfully" , category="success")
            pass
    if request.method == "POST":
        emailAddress = request.form.get('username')
        password = request.form.get('password')
        
        emailChecker = User.query.filter_by(emailAddress=emailAddress).first()
        
        if emailChecker:
            if check_password_hash(emailChecker.password,password):
                session.permanent = True
                session["emailAddress"] = emailChecker.emailAddress
                session["accountType"] = emailChecker.account_type
                
                if "emailAddress" in session and session["accountType"] == "User":
                    flash("Login Successfully" , category="success")
                    pass

                if "emailAddress" in session and session["accountType"] == "Admin":
                    flash("Login Successfully" , category="success")
                    pass
                

            else:
                flash("Password is incorrect", category="error")        
        else:
            flash("No such thing as that email address registered!", category="error")   
            
    pass


@auth.route('/logout')
def logoutUser():
    session.clear()
    flash("Log out Successfully", category="error")
    pass

@auth.route('/delete/<int:id>')
def DeleteUser(id:int):
    delete_task = User.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        pass
    except Exception as e:
        return f"ERROR{e}"
