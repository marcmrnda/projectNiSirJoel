from flask import render_template,Blueprint,request,redirect,flash,url_for,session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .model.user import User, Record
from . import db
from flask_cors import CORS
import os
import re
import smtplib
from dotenv import load_dotenv
import secrets
import string
from datetime import datetime
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

auth = Blueprint('auth',__name__)


CORS(auth, resources={r"/*": {"origins": "*"}})

load_dotenv()  
# Load credentials from environment
email_user = os.getenv("EMAIL_USER")
email_password = os.getenv("EMAIL_PASSWORD") 

# --- Load Models Once at Startup ---
print("Loading models and training columns...")
try:
    meta_model = joblib.load('C:/dev/projects/sirJoelProject/app/AIMODEL/meta_model.pkl')
    model1 = joblib.load('C:/dev/projects/sirJoelProject/app/AIMODEL/base_model1.pkl')
    model2 = joblib.load('C:/dev/projects/sirJoelProject/app/AIMODEL/base_model2.pkl') 
    model3 = joblib.load('C:/dev/projects/sirJoelProject/app/AIMODEL/base_model3.pkl')
    training_columns = joblib.load('C:/dev/projects/sirJoelProject/app/AIMODEL/training_columns.pkl')
    MODELS_LOADED = True
    print("✓ All models loaded successfully!")
except FileNotFoundError:
    print("❌ Model files not found. Please train and save them first.")
    MODELS_LOADED = False

# --- Helper Function for Prediction ---
def predict_student_stacked(student_dict):
    """Predicts enrollment for a single student."""
    if not MODELS_LOADED:
        raise RuntimeError("Models are not loaded.")

    try:
        df = pd.DataFrame([student_dict])
        df_encoded = pd.get_dummies(df)
        df_encoded = df_encoded.reindex(columns=training_columns, fill_value=0)
        
        base_pred1 = model1.predict_proba(df_encoded)[:, 1]
        base_pred2 = model2.predict_proba(df_encoded)[:, 1]
        base_pred3 = model3.predict_proba(df_encoded)[:, 1]
        
        prediction_stack = np.column_stack([base_pred1, base_pred2, base_pred3])
        
        final_prediction = meta_model.predict(prediction_stack)[0]
        final_probabilities = meta_model.predict_proba(prediction_stack)[0]
        
        prediction_percentage = final_probabilities * 100
        confidence = max(final_probabilities)
        
        return {
            "prediction_result": prediction_percentage,
            "confidence": float(confidence)
        }
    except Exception as e:
        raise RuntimeError(f"Error during prediction: {str(e)}")


def send_welcome_email(emailAddress, password):
    # Create the email
    msg = MIMEMultipart("alternative")
    msg["From"] = email_user
    msg["To"] = emailAddress
    msg["Subject"] = "Your Account Password"

    # Plain text fallback
    text = f"""\
    Your account has been created successfully.
    Your password is: {password}
    Please change your password after logging in.
    """

    # HTML version
    html = f"""\
    <html>
      <body>
        <h2 style="color:#4CAF50;">Welcome to Our App 🎉</h2>
        <p>Your account has been created successfully.</p>
        <p><b>Password:</b> {password}</p>
        <p style="color:red;">⚠ Please change your password after logging in.</p>
      </body>
    </html>
    """

    # Attach both plain and HTML
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send via Gmail SMTP
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(email_user, email_password)
        s.sendmail(email_user, emailAddress, msg.as_string())


def generate_crypto_token(length=8):
    alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))





@auth.route('/register', methods=["POST","GET"])
def register():
    if request.method == "POST":
            #user details
            firstName = request.form.get('firstName')
            middleName = request.form.get('middleName')
            lastName = request.form.get('lastName')
            dateOfBirth = request.form.get('dateOfBirth')
            sex = request.form.get('sex')
            emailAddress = request.form.get('emailAddress')
            student_ID = request.form.get('student_ID')
            mobileNumber = request.form.get('mobileNumber')
            #record details
            campus = request.form.get('campus')
            academic_year = request.form.get('academic_year')
            academic_term = request.form.get('academic_term')
            course_1st = request.form.get('course_1st')
            course_2nd = request.form.get('course_2nd')
            birth_city = request.form.get('birth_city')
            birth_province = request.form.get('birth_province')
            birth_country = request.form.get('birth_country')
            gender = request.form.get('gender')
            citizen_of = request.form.get('citizen_of')
            curr_region = request.form.get('curr_region')
            curr_province = request.form.get('curr_province')
            curr_city = request.form.get('curr_city')
            curr_brgy = request.form.get('curr_brgy')
            curr_street = request.form.get('curr_street')
            curr_postal = request.form.get('curr_postal')
            per_country = request.form.get('per_country')
            per_region = request.form.get('per_region')
            per_province = request.form.get('per_province')
            per_city = request.form.get('per_city')
            per_brgy = request.form.get('per_brgy')
            per_street = request.form.get('per_street')
            per_postal = request.form.get('per_postal')
            religion = request.form.get('religion')
            civil_status = request.form.get('civil_status')
            student_type = request.form.get('student_type')
            last_school_attended = request.form.get('last_school_attended')
            school_type = request.form.get('school_type')
            
            student_dict = {    
                "Program (First Choice)": course_1st.lower(),
                "Program (Second Choice)": course_2nd.lower(),
                "Current Region": curr_region.lower(),
                "Current Province": curr_province.lower(),
                "City/Municipality": curr_city.lower(),
                "Permanent Country": per_country.lower(),
                "Student Type": student_type.lower(),
                "Last School Attended": last_school_attended.lower(),
                "School Type": school_type.lower()
            }
            
            results = predict_student_stacked(student_dict)
            
            
            birth_date = datetime.strptime(dateOfBirth, "%m/%d/%Y").date()
            
            emailChecker = User.query.filter_by(emailAddress=emailAddress).first()
            
            if emailChecker:
                flash("Email Address already taken", category="error")
            else:
                # Example usage
                passwordGeneration = generate_crypto_token()
                new_user = User(firstName=firstName, middleName=middleName, lastName=lastName, dateOfBirth=birth_date, emailAddress=emailAddress, password=generate_password_hash(passwordGeneration,method='pbkdf2:sha256'),
                                sex=sex, student_ID=student_ID, mobileNumber=mobileNumber)
                db.session.add(new_user)
                db.session.commit()
                
                newUserChecker = User.query.filter_by(emailAddress=emailAddress).first()
                
                if newUserChecker:
                 
                    new_record = Record(user_id=newUserChecker.user_id, campus=campus, academic_year=academic_year, academic_term=academic_term, course_1st=course_1st, course_2nd=course_2nd,
                                         birth_city=birth_city, birth_province=birth_province, birth_country=birth_country,
                                         gender=gender, citizen_of=citizen_of,
                                         curr_region=curr_region, curr_province=curr_province, curr_city=curr_city, curr_brgy=curr_brgy, curr_street=curr_street, curr_postal=curr_postal,
                                         per_country=per_country, per_region=per_region, per_province=per_province, per_city=per_city, per_brgy=per_brgy, per_street=per_street, per_postal=per_postal,
                                         religion=religion, civil_status=civil_status, student_type=student_type, last_school_attended=last_school_attended, school_type=school_type,prediction_result=results['prediction_result'][1], confidence=results['confidence']
                )
                    db.session.add(new_record)
                    db.session.commit()
                    
                    send_welcome_email(newUserChecker.emailAddress, passwordGeneration)
                    return jsonify({"message":"Account Created your password is sent on your email address"}), 201
                
                else:
                    flash("Error creating user record", category="error")
                
                
                
               
                
                
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
        emailAddress = request.form.get('emailAddress')
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
            
    return jsonify({"message":"Account hatdog"}), 201


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
