from flask import Flask, render_template, request, redirect, flash
from DBConnection import Db
from email.mime import image
import os, datetime, csv
from flask import Flask, render_template, request, redirect,session
import smtplib
from email.mime.text import MIMEText
from flask_mail import Mail
from random import randint

from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
# from tkinter import *
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
app.secret_key="kmsoe89j42"

path1=r"C:\Users\user\Documents\PROGRAMS\PycharmProjects\DiseasePredictionApp\static\images\\"
path2=r"C:\Users\user\Documents\PROGRAMS\PycharmProjects\dps_email\dps_email.txt"
path3=r"C:\Users\user\Documents\PROGRAMS\PycharmProjects\DiseasePredictionApp\static\dataset\\"

"""
import bcrypt
password = b"secretPass123"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed)
if bcrypt.checkpw(password, hashed):
    print("It matches.")
else:
    print("Didn't match!")
"""
########################################################################################################################

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login_post', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    db = Db()
    qry = db.selectOne("SELECT * FROM login WHERE username='"+username+"' AND password ='"+password+"'")
    if qry is not None and qry['user_type'] == 'admin':
        session['lid'] = qry["login_id"]
        return redirect('/admin_home')
    elif qry is not None and qry['user_type'] == 'user':
        session['lid'] = qry["login_id"]
        return redirect('/user_home')
    elif qry is not None and (qry['user_type'] == 'doctor' or qry['user_type'] == 'pending'):
        session['lid'] = qry["login_id"]
        return redirect('/doctor_home')
    else:
        return "<script>alert('Username/Password mismatch!!'); window.location='/'</script>"

@app.route('/logout')
def logout():
    session.pop('lid', None)
    flash('You were logged out.')
    return redirect('/')

@app.route('/signup_post', methods=['post'])
def signup_post():
    user_type = request.form['sign-up']
    if user_type == "user":
        return render_template('user/user_register.html')
    elif user_type == "doctor":
        return render_template('doctor/doctor_register.html')

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/forgot_password_post", methods=["POST"])
def forgot_password_post():
    recovery_email = request.form['recovery-email']
    db = Db()
    qry = db.selectOne("SELECT * FROM login, user WHERE login.login_id = user.user_id AND user.email_address = '" + recovery_email + "'")
    if qry is not None:
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)

            gmail.ehlo()

            gmail.starttls()

            with open(path2) as f:
                dp_email = f.readline()
                dp_email_password = f.readline()
                gmail.login(dp_email, dp_email_password)

        except Exception as e:
            print("Couldn't setup email!!" + str(e))

        otpvalue = randint(1000, 9999)

        msg = MIMEText(f"Your OTP is {otpvalue}")

        msg['Subject'] = 'Verification'

        email = recovery_email

        msg['To'] = email

        msg['From'] = dp_email

        try:

            gmail.send_message(msg)

        except Exception as e:

            print("COULDN'T SEND EMAIL", str(e))

        session['otp'] = otpvalue

        return reset_password()
    else:
        return "<script>alert('Email Address doesn't exists!!'); window.location='/forgot_password'</script>"

@app.route("/reset_password")
def reset_password():
    return render_template("reset_password.html")

@app.route("/reset_password_post", methods=["POST"])
def reset_password_post():
    reset_code = request.form['reset-code']
    new_password = request.form['new-password']
    re_new_password = request.form['re-new-password']
    if reset_code == str(session['otp']):
        if new_password == re_new_password:
            db = Db()
            qry = db.update("UPDATE login SET password = '" + new_password + "' WHERE login_id = '" + str(session['lid']) + "'")
            return "<script>alert('Your Account has been reset Successfully'); window.location='/'</script>"
        else:
            return "<script>alert('Password mismatch!'); window.location='/reset_password'</script>"
    else:
        return "<script>alert('Incorrect Code!'); window.location='/reset_password'</script>"

    return render_template("/reset_password")

@app.route('/change_pass')
def change_pass():
    return render_template("change_pass.html")

@app.route('/change_pass_post', methods=['POST'])
def change_pass_post():
    current_pass = request.form['current-pass']
    new_pass = request.form['new-password']
    re_new_pass = request.form['re-new-password']
    db = Db()
    lid = session.get('lid')
    qry = db.selectOne("SELECT * FROM login WHERE login_id = '"+str(lid)+"'")
    if qry is not None:
        if qry["password"] == current_pass:
            if new_pass == re_new_pass:
                qry = db.update("UPDATE login SET password = '"+new_pass+"' WHERE login_id = '"+str(lid)+"'")
                return "<script>alert('Succesfully Changed'); window.location='/'</script>"
            else:
                return "<script>alert('New password mismatch!!'); window.location='/change_pass'</script>"
        else:
            return "<script>alert('Incorrect old password!!'); window.location='/change_pass'</script>"


############     A D M I N     #########################################################################################

@app.route('/admin_home')
def admin_home():
    return render_template("admin/admin_home.html")

@app.route('/dataset')
def dataset():
    db = Db()
    qry = db.select("SELECT * FROM disease_dataset")
    symptoms = []
    for i in range(len(qry)):
        symptoms.append(qry[i]["symptoms"].split(","))
    return render_template("admin/manage_dataset.html", qry=qry, symptoms=symptoms)

@app.route('/add_dataset', methods=['post'])
def add_dataset():
    csv_file = request.files['dataset_csv']
    dates = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    path = path1 + dates + ".csv"
    csv_file.save(path)
    csv_dicts = []
    with open(path, mode='r') as file:
        for row in csv.DictReader(file):
            csv_dicts.append(dict(row))
    db = Db()
    for data in csv_dicts:
        qry = db.insert("INSERT INTO disease_dataset VALUES('','" + data['disease'] + "', '" + data['category'] + "','" + data['symptom'] + "','" + data['count_of_disease_occurrence'] + "')")
    return redirect('/dataset')

@app.route('/edit_dataset/<i>')
def edit_dataset(i):
    db = Db()
    qry = db.selectOne("SELECT * FROM disease_dataset WHERE dataset_id = '" + i + "'")
    return render_template('admin/dataset_edit.html', qry=qry)

@app.route('/edit_dataset_post/<i>', methods=['post'])
def edit_dataset_post(i):
    disease_name = request.form['disease_name']
    category = request.form['category']
    symptoms = request.form['symptoms']
    count = request.form['count']
    db = Db()
    qry = db.update("UPDATE disease_dataset SET disease = '" + disease_name + "', category = '" + category + "', symptoms = '" + symptoms + "', count_of_occurrence = '" + count + "' WHERE dataset_id = '" + i + "'")
    return redirect('/dataset')

@app.route('/doctors')
def doctors():
    db = Db()
    qry1 = db.select("SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type != 'rejected'")
    return render_template("admin/view_doctors.html", qry1=qry1)

@app.route('/pending_dr')
def pending_dr():
    db = Db()
    qry1 = db.select("SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'pending'")
    return render_template("admin/pending_dr.html", qry1=qry1)

@app.route('/search_pending_dr', methods=['post'])
def search_pending_dr():
    text = request.form['search_pending_dr']
    db = Db()
    qry = db.select("SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'pending' AND doctor.name like '%"+text+"%'")
    return render_template('admin/pending_dr.html', qry1=qry)

@app.route('/patients')
def patients():
    db = Db()
    qry1 = db.select("SELECT * FROM user, login WHERE user.user_id = login.login_id AND login.user_type = 'user'")
    return render_template("admin/view_patients.html", qry1=qry1)

@app.route('/search_user', methods=['POST'])
def search_user():
    text = request.form['search_patient']
    db = Db()
    qry = db.select("SELECT * FROM user, login WHERE user.`user_id` = login.`login_id` AND user_type = 'user' AND user.name like '%"+text+"%'")
    return render_template('admin/view_patients.html', qry1=qry)

@app.route('/approve_dr/<i>')
def approve_dr(i):
    db = Db()
    qry = db.update("UPDATE login SET `user_type` = 'doctor' WHERE login_id = '"+i+"'")
    return doctors()

@app.route('/reject_dr/<i>')
def reject_dr(i):
    db = Db()
    qry = db.update("UPDATE login SET `user_type` = 'rejected' WHERE login_id = '"+i+"'")
    return doctors()

@app.route('/search_dr', methods=['POST'])
def search_dr():
    text = request.form['search_doctor']
    db = Db()
    qry = db.select("SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type != 'rejected' AND name like '%"+text+"%'")
    return render_template('admin/view_doctors.html', qry1=qry)

@app.route('/view_more_dr/<i>')
def view_more_dr(i):
    db = Db()
    qry = db.selectOne("SELECT * FROM doctor WHERE doctor_id = '"+i+"'")
    return render_template("admin/view_more_doctor.html", qry=qry)

@app.route('/feedbacks')
def feedbacks():
    db = Db()
    qry = db.select("SELECT * FROM login, feedbacks WHERE login.login_id = feedbacks.user_id AND login.user_type='user'")
    return render_template("admin/view_feedbacks.html", qry=qry)


############     D O C T O R     #######################################################################################

@app.route('/doctor_register', methods=['post'])
def doctor_register():
    username = request.form['username']
    email = request.form['email']
    name = request.form['name']
    photo = request.files['dr-photo']
    dob = request.form['dob']
    address = request.form['address']
    contact_number = request.form['contact-number']
    license_id = request.form['license-id']
    qualification = request.form['qualification']
    category = request.form.getlist('category')
    category = ','.join(category)
    admission_fee = request.form['admission-fee']
    pro_started_yr = request.form['pro-started-yr']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    password = request.form['password']
    re_password = request.form['re-password']
    dates = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    photo.save(path1 + dates + ".jpg")
    path = "/static/images/" + dates + ".jpg"

    db = Db()
    qry2 = db.select("SELECT * FROM login WHERE username = '"+username+"'")
    if len(qry2) > 0:
        return "<script>alert('Username already exist!'); window.location='/'</script>"
    else:
        if password == re_password:
            qry = db.insert("INSERT INTO login VALUES('','" + username + "', '" + password + "', 'pending')")
            qry1 = db.insert(
                "INSERT INTO doctor VALUES('" + str(
                    qry) + "','" + username + "', '" + email + "', '" + name + "', '" + path + "', '" + dob + "', '" + address + "', '" + contact_number + "', '" + license_id + "', '" + qualification + "', '" + category + "', '" + admission_fee + "', '" + pro_started_yr + "')")
            qry3 = db.insert(
                "INSERT INTO location VALUES('','" + str(qry) + "', '" + longitude + "', '" + latitude + "')")
            return redirect('/')
        else:
            return "<script>alert('Password mismatch!'); window.location='/signup_post'</script>"

@app.route('/doctor_home')
def doctor_home():
    return render_template('doctor/doctor_home.html')

@app.route('/doctor_schedule')
def doctor_schedule():
    db = Db()
    qry = db.select("SELECT * FROM schedule WHERE doctor_id='"+str(session['lid'])+"' ORDER BY schedule_date desc")
    return render_template('doctor/doctor_schedule.html', qry=qry)

@app.route('/doctor_schedule_add')
def doctor_schedule_add():
    return render_template('doctor/doctor_schedule_add.html')

@app.route('/doctor_schedule_add_post', methods=['post'])
def doctor_schedule_add_post():
    schedule_date = request.form['schedule_date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    import datetime
    # schedule_date="2021-04-10"
    year, month, day = (int(x) for x in schedule_date.split('-'))
    ans = datetime.date(year, month, day)
    print(ans.strftime("%A"))
    schedule_day =ans.strftime("%A")
    status = "Active"
    db = Db()
    db.insert("INSERT INTO schedule VALUES('', '"+str(session['lid'])+"', '"+schedule_date+"','"+schedule_day+"', '"+start_time+"', '"+end_time+"', '"+status+"')")
    return doctor_schedule()

@app.route('/appointment')
def appointment():

    return render_template('doctor/appointment.html')

@app.route('/view_dr_profile')
def view_dr_profile():
    db=Db()
    lid=session['lid']
    qry=db.selectOne("select * from doctor where doctor_id='"+str(lid)+"'")
    this_year = datetime.date.today().year
    age = this_year - int(qry['date_of_birth'].split('-')[0])
    return render_template("doctor/view_doctor_profile.html",q=qry, age=age)

@app.route('/edit_dr')
def edit_dr():
    db = Db()
    lid = session['lid']
    qry = db.selectOne("select * from doctor where doctor_id='" + str(lid) + "'")
    category = qry['category'].split(',')
    return render_template("doctor/edit_doctor_profile.html", data=qry, category=category)

@app.route('/edit_dr_post', methods=['post'])
def edit_dr_post():
    username = request.form['username']
    email = request.form['email']
    name = request.form['name']
    photo = request.files['dr-photo']
    dob = request.form['dob']
    address = request.form['address']
    contact_number = request.form['contact-number']
    license_id = request.form['license-id']
    qualification = request.form['qualification']
    category = request.form.getlist('category')
    category = ','.join(category)
    admission_fee = request.form['admission-fee']
    pro_started_yr = request.form['pro-started-yr']
    dates=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    photo.save(path1+dates+".jpg")
    path="/static/images/"+dates+".jpg"
    db=Db()
    if request.files is not None:
        if photo.filename != "":
            qry=db.update("UPDATE `doctor` SET `username`='"+username+"',`email_address`='"+email+"',`name`='"+name+"',`photo`='"+path+"',`date_of_birth`='"+dob+"',`address`='"+address+"',`contact_number`='"+contact_number+"',`license_id`='"+license_id+"',`qualification`='"+qualification+"',`category`='"+category+"',`admission_fee`='"+admission_fee+"',`pro_started_yr`='"+pro_started_yr+"' WHERE `doctor_id`='"+str(session['lid'])+"'")
        else:
            qry = db.update(
                "UPDATE `doctor` SET `username`='" + username + "',`email_address`='" + email + "',`name`='" + name + "',`date_of_birth`='" + dob + "',`address`='" + address + "',`contact_number`='" + contact_number + "',`license_id`='" + license_id + "',`qualification`='" + qualification + "',`category`='" + category + "',`admission_fee`='" + admission_fee + "',`pro_started_yr`='" + pro_started_yr + "' WHERE `doctor_id`='" + str(
                    session['lid']) + "'")
    else:
        qry = db.update(
            "UPDATE `doctor` SET `username`='" + username + "',`email_address`='" + email + "',`name`='" + name + "',`date_of_birth`='" + dob + "',`address`='" + address + "',`contact_number`='" + contact_number + "',`license_id`='" + license_id + "',`qualification`='" + qualification + "',`category`='" + category + "',`admission_fee`='" + admission_fee + "',`pro_started_yr`='" + pro_started_yr + "' WHERE `doctor_id`='" + str(
                session['lid']) + "'")
    return view_dr_profile()


############     U S E R     ###########################################################################################

@app.route('/user_register', methods=['post'])
def user_register():
    username = request.form['username']
    name = request.form['name']
    photo = request.files['photo']
    phone_number = request.form['phone-number']
    email = request.form['email']
    home = request.form['home']
    place = request.form['place']
    post = request.form['post']
    pin = request.form['pin']
    dob = request.form['dob']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    password = request.form['password']
    re_password = request.form['re-password']
    dates = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    photo.save(path1 + dates + ".jpg")
    path = "/static/images/" + dates + ".jpg"

    db = Db()
    qry2 = db.select("SELECT * FROM login WHERE username = '"+username+"'")
    if len(qry2) > 0:
        return "<script>alert('Username already exist!'); window.location='/'</script>"
    else:
        if password == re_password:
            qry = db.insert("INSERT INTO login VALUES('','" + username + "', '" + password + "', 'user')")
            qry1 = db.insert(
                "INSERT INTO user VALUES('" + str(
                    qry) + "','" + username + "', '" + email + "', '" + name + "', '" + path + "', '" + home + "', '" + dob + "', '" + phone_number + "', '" + place + "', '" + pin + "', '" + post + "')")

            qry3 = db.insert("INSERT INTO location VALUES('','" + str(qry) + "', '"+longitude+"', '"+latitude+"')")
            return redirect('/')
        else:
            return "<script>alert('Password mismatch!'); window.location='/signup_post'</script>"

@app.route('/user_home')
def user_home():
    return render_template("user/user_home.html")

@app.route('/view_user_profile')
def view_user_profile():
    db=Db()
    lid=session['lid']
    qry=db.selectOne("select * from user where user_id='"+str(lid)+"'")
    this_year = datetime.date.today().year
    age = this_year - int(qry['date_of_birth'].split('-')[0])
    return render_template("user/view_user_profile.html",q=qry, age=age)

@app.route('/edit_user')
def edit_user():
    db = Db()
    lid = session['lid']
    qry = db.selectOne("select * from user where user_id='"+str(lid)+"'")
    return render_template("user/edit_user_profile.html",data=qry)

@app.route('/edituserpost',methods=['post'])
def edituserpost():
    username=request.form['textfield']
    name=request.form['textfield2']
    photo=request.files['photo']
    home=request.form['home']
    place=request.form['textfield3']
    post=request.form['post']
    pin=request.form['pin']
    phone_number=request.form['phone_number']
    email=request.form['email']
    date_of_birth=request.form['dob']
    dates=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    photo.save(path1+dates+".jpg")
    path="/static/images/"+dates+".jpg"
    db=Db()
    if request.files is not None:
        if photo.filename != "":
            qry=db.update("UPDATE login, user SET login.username='"+username+"',user.email_address='"+email+"',user.name='"+name+"', user.photo='"+path+"', user.home='"+home+"', user.date_of_birth='"+date_of_birth+"',user.mobile_number='"+phone_number+"',user.place='"+place+"',user.pin='"+pin+"',user.post='"+post+"' WHERE login.login_id = user.user_id AND login.login_id='"+str(session.get('lid'))+"'")
        else:
            qry=db.update("UPDATE login, user SET login.username='"+username+"',user.email_address='"+email+"',user.name='"+name+"', user.home='"+home+"', user.date_of_birth='"+date_of_birth+"',user.mobile_number='"+phone_number+"',user.place='"+place+"',user.pin='"+pin+"',user.post='"+post+"' WHERE login.login_id = user.user_id AND login.login_id='"+str(session.get('lid'))+"'")
    else:
            qry=db.update("UPDATE login, user SET login.username='"+username+"',user.email_address='"+email+"',user.name='"+name+"', user.home='"+home+"', user.date_of_birth='"+date_of_birth+"',user.mobile_number='"+phone_number+"',user.place='"+place+"',user.pin='"+pin+"',user.post='"+post+"' WHERE login.login_id = user.user_id AND login.login_id='"+str(session.get('lid'))+"'")
    return view_user_profile()

@app.route('/nearestservice',methods=['get'])
def nearestservice():
    db = Db()
    user_loc = db.selectOne("SELECT * FROM location WHERE location.login_id = '"+str(session['lid'])+"'")
    #doc_loc = db.select("SELECT * FROM login, location WHERE location.login_id = login.login_id AND login.user_type = 'doctor'")
    #print(doc_loc)
    print(user_loc)
    qry=db.select("SELECT  (3959 * ACOS ( COS ( RADIANS('"+str(user_loc['latitude'])+"') ) * COS( RADIANS( location.latitude) ) * COS( RADIANS( location.longitude ) - RADIANS('"+str(user_loc['longitude'])+"') ) + SIN ( RADIANS('"+str(user_loc['latitude'])+"') ) * SIN( RADIANS(  location.latitude ) ))) AS user_distance,doctor.* FROM doctor, login, location WHERE doctor.doctor_id = login.login_id AND location.login_id = login.login_id AND login.user_type = 'doctor' HAVING user_distance  < 10.2137")
    print(qry)
    return "ok"


@app.route('/add_symptoms')
def add_symptoms():
    # List of the symptoms is listed here in list l1.

    l1 = ['back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine',
          'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach',
          'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation',
          'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs',
          'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool',
          'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps', 'bruising', 'obesity', 'swollen_legs',
          'swollen_blood_vessels', 'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails',
          'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts', 'drying_and_tingling_lips',
          'slurred_speech', 'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
          'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness',
          'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine',
          'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
          'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain',
          'abnormal_menstruation', 'dischromic _patches', 'watering_from_eyes', 'increased_appetite', 'polyuria',
          'family_history', 'mucoid_sputum',
          'rusty_sputum', 'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion',
          'receiving_unsterile_injections', 'coma', 'stomach_bleeding', 'distention_of_abdomen',
          'history_of_alcohol_consumption', 'fluid_overload', 'blood_in_sputum', 'prominent_veins_on_calf',
          'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
          'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose',
          'yellow_crust_ooze']
    l1 = sorted(l1)
    return render_template('user/add_symtoms.html', l1=l1)

# @app.route('/dp_post', methods=['post'])
# def dp_post():
#     sym1 = request.form['symptoms1']
#     sym2 = request.form['symptoms2']
#     sym3 = request.form['symptoms3']
#     sym4 = request.form['symptoms4']
#     sym5 = request.form['symptoms5']
#
#     syms = f"{sym1},{sym2},{sym3},{sym4},{sym5}"
#     dates = datetime.datetime.now().strftime("%Y-%m-%d.%H:%M:%S")
#     db = Db()
#     sym_row = db.insert("INSERT INTO symptoms VALUES('','" + str(session['lid']) + "', '" + syms + "', '"+dates+"')")
#     session['sym_row'] = sym_row
#     return redirect('/dp_result')


@app.route('/disease_prediction',methods=['post'])
def disease_prediction():
    l1 = ['back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine',
          'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach',
          'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation',
          'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs',
          'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool',
          'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps', 'bruising', 'obesity', 'swollen_legs',
          'swollen_blood_vessels', 'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails',
          'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts', 'drying_and_tingling_lips',
          'slurred_speech', 'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
          'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness',
          'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine',
          'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
          'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain',
          'abnormal_menstruation', 'dischromic _patches', 'watering_from_eyes', 'increased_appetite', 'polyuria',
          'family_history', 'mucoid_sputum',
          'rusty_sputum', 'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion',
          'receiving_unsterile_injections', 'coma', 'stomach_bleeding', 'distention_of_abdomen',
          'history_of_alcohol_consumption', 'fluid_overload', 'blood_in_sputum', 'prominent_veins_on_calf',
          'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
          'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose',
          'yellow_crust_ooze']

    disease = ['Fungal infection', 'Allergy', 'GERD', 'Chronic cholestasis', 'Drug Reaction',
               'Peptic ulcer diseae', 'AIDS', 'Diabetes', 'Gastroenteritis', 'Bronchial Asthma', 'Hypertension',
               ' Migraine', 'Cervical spondylosis',
               'Paralysis (brain hemorrhage)', 'Jaundice', 'Malaria', 'Chicken pox', 'Dengue', 'Typhoid', 'hepatitis A',
               'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E', 'Alcoholic hepatitis', 'Tuberculosis',
               'Common Cold', 'Pneumonia', 'Dimorphic hemmorhoids(piles)',
               'Heartattack', 'Varicoseveins', 'Hypothyroidism', 'Hyperthyroidism', 'Hypoglycemia', 'Osteoarthristis',
               'Arthritis', '(vertigo) Paroymsal  Positional Vertigo', 'Acne', 'Urinary tract infection', 'Psoriasis',
               'Impetigo']

    l2 = []
    for x in range(0, len(l1)):
        l2.append(0)

    # TESTING DATA df -------------------------------------------------------------------------------------
    df = pd.read_csv(path3 + "Training.csv")

    df.replace(
        {'prognosis': {'Fungal infection': 0, 'Allergy': 1, 'GERD': 2, 'Chronic cholestasis': 3, 'Drug Reaction': 4,
                       'Peptic ulcer diseae': 5, 'AIDS': 6, 'Diabetes ': 7, 'Gastroenteritis': 8, 'Bronchial Asthma': 9,
                       'Hypertension ': 10,
                       'Migraine': 11, 'Cervical spondylosis': 12,
                       'Paralysis (brain hemorrhage)': 13, 'Jaundice': 14, 'Malaria': 15, 'Chicken pox': 16,
                       'Dengue': 17, 'Typhoid': 18, 'hepatitis A': 19,
                       'Hepatitis B': 20, 'Hepatitis C': 21, 'Hepatitis D': 22, 'Hepatitis E': 23,
                       'Alcoholic hepatitis': 24, 'Tuberculosis': 25,
                       'Common Cold': 26, 'Pneumonia': 27, 'Dimorphic hemmorhoids(piles)': 28, 'Heart attack': 29,
                       'Varicose veins': 30, 'Hypothyroidism': 31,
                       'Hyperthyroidism': 32, 'Hypoglycemia': 33, 'Osteoarthristis': 34, 'Arthritis': 35,
                       '(vertigo) Paroymsal  Positional Vertigo': 36, 'Acne': 37, 'Urinary tract infection': 38,
                       'Psoriasis': 39,
                       'Impetigo': 40}}, inplace=True)

    # print(df.head())

    X = df[l1]

    y = df[["prognosis"]]
    np.ravel(y)
    # print(y)

    # TRAINING DATA tr --------------------------------------------------------------------------------
    tr = pd.read_csv(path3 + "Testing.csv")
    tr.replace(
        {'prognosis': {'Fungal infection': 0, 'Allergy': 1, 'GERD': 2, 'Chronic cholestasis': 3, 'Drug Reaction': 4,
                       'Peptic ulcer diseae': 5, 'AIDS': 6, 'Diabetes ': 7, 'Gastroenteritis': 8, 'Bronchial Asthma': 9,
                       'Hypertension ': 10,
                       'Migraine': 11, 'Cervical spondylosis': 12,
                       'Paralysis (brain hemorrhage)': 13, 'Jaundice': 14, 'Malaria': 15, 'Chicken pox': 16,
                       'Dengue': 17, 'Typhoid': 18, 'hepatitis A': 19,
                       'Hepatitis B': 20, 'Hepatitis C': 21, 'Hepatitis D': 22, 'Hepatitis E': 23,
                       'Alcoholic hepatitis': 24, 'Tuberculosis': 25,
                       'Common Cold': 26, 'Pneumonia': 27, 'Dimorphic hemmorhoids(piles)': 28, 'Heart attack': 29,
                       'Varicose veins': 30, 'Hypothyroidism': 31,
                       'Hyperthyroidism': 32, 'Hypoglycemia': 33, 'Osteoarthristis': 34, 'Arthritis': 35,
                       '(vertigo) Paroymsal  Positional Vertigo': 36, 'Acne': 37, 'Urinary tract infection': 38,
                       'Psoriasis': 39,
                       'Impetigo': 40}}, inplace=True)

    X_test = tr[l1]
    y_test = tr[["prognosis"]]
    np.ravel(y_test)

    symptoms1 = request.form['symptoms1']
    symptoms2 = request.form['symptoms2']
    symptoms3 = request.form['symptoms3']
    symptoms4 = request.form['symptoms4']
    symptoms5 = request.form['symptoms5']
    symptoms = [symptoms1, symptoms2, symptoms3, symptoms4, symptoms5]


    # if symptoms1 not in l1 or symptoms2 not in l1 or symptoms3 not in l1:
    #     return render_template("user/disease_prediction_result.html", res1="False", qry=symptoms)

    # sym_valid = [True for sym in symptoms if sym in l1]
    # print(sym_valid)


    res1=DecisionTree(symptoms1, symptoms2, symptoms3, symptoms4, symptoms5, X, y, X_test, y_test, l1, disease, l2)
    res2=randomforest(symptoms1, symptoms2, symptoms3, symptoms4, symptoms5, X, y, X_test, y_test, l1, disease, l2)
    res3=NaiveBayes(symptoms1, symptoms2, symptoms3, symptoms4, symptoms5, X, y, X_test, y_test, l1, disease, l2)

    syms = f"{symptoms1},{symptoms2},{symptoms3},{symptoms4},{symptoms5}"
    algo = ["Decision Tree", "Random Forest", "Naive Bayes"]
    predictions = f"{algo[0]}:{res1},{algo[1]}:{res2},{algo[2]}:{res3}"
    print(predictions)
    print(type(predictions))
    dates = datetime.datetime.now().strftime("%Y-%m-%d.%H:%M:%S")
    db = Db()
    db.insert("INSERT INTO prediction_results VALUES('','" + str(session['lid']) + "', '" + syms + "', '" + predictions + "', '"+dates+"')")
    qry1 = db.select("SELECT * FROM login, doctor WHERE login.login_id=doctor.doctor_id AND login.user_type='doctor'")

    return render_template("user/disease_prediction_result.html", res1=res1, res2=res2, res3=res3, qry=symptoms, qry1=qry1)




def DecisionTree(symptom1=None, symptom2=None, symptom3=None, symptom4=None, symptom5=None, X=None, y=None, X_test=None, y_test=None, l1=None, disease=None, l2=None):

    from sklearn import tree

    clf3 = tree.DecisionTreeClassifier()   # empty model of the decision tree
    clf3 = clf3.fit(X,y)

    # calculating accuracy-----------------------------------------------------------------
    from sklearn.metrics import accuracy_score
    y_pred=clf3.predict(X_test)
    print(accuracy_score(y_test, y_pred))
    print(accuracy_score(y_test, y_pred,normalize=False))
    # -------------------------------------------------------------------------------------

    psymptoms = [symptom1,symptom2,symptom3,symptom4,symptom5]
    # print(psymptoms)
    for k in range(0,len(l1)):
        # print (k,)
        for z in psymptoms:
            if(z==l1[k]):
                l2[k]=1

    inputtest = [l2]
    print(inputtest)
    predict = clf3.predict(inputtest)
    predicted=predict[0]
    return disease[predicted]
    # for a in predict:
    #     print(str(disease[a]))
    #
    # h='no'
    # for a in range(0,len(disease)):
    #     if(predicted == a):
    #         h='yes'
    #         break
    #     return disease[a]
    # if (h=='yes'):
    #     t1.delete("1.0", END)
    #     t1.insert(END, disease[a])
    # else:
    #     t1.delete("1.0", END)
    #     t1.insert(END, "Not Found")
#
def randomforest(symptom1=None, symptom2=None, symptom3=None, symptom4=None, symptom5=None, X=None, y=None, X_test=None, y_test=None, l1=None, disease=None, l2=None):
    from sklearn.ensemble import RandomForestClassifier
    clf4 = RandomForestClassifier()
    clf4 = clf4.fit(X,np.ravel(y))

    # calculating accuracy-------------------------------------------------------------------
    from sklearn.metrics import accuracy_score
    y_pred=clf4.predict(X_test)
    print(accuracy_score(y_test, y_pred))
    print(accuracy_score(y_test, y_pred,normalize=False))
    # -----------------------------------------------------

    psymptoms = [symptom1,symptom2,symptom3,symptom4,symptom5]

    for k in range(0,len(l1)):
        for z in psymptoms:
            if(z==l1[k]):
                l2[k]=1

    inputtest = [l2]
    predict = clf4.predict(inputtest)
    predicted=predict[0]
    return disease[predicted]

    # h='no'
    # for a in range(0,len(disease)):
    #     if(predicted == a):
    #         h='yes'
    #         break
    #
    # if (h=='yes'):
    #     t2.delete("1.0", END)
    #     t2.insert(END, disease[a])
    # else:
    #     t2.delete("1.0", END)
    #     t2.insert(END, "Not Found")
#
#
def NaiveBayes(symptom1=None, symptom2=None, symptom3=None, symptom4=None, symptom5=None, X=None, y=None, X_test=None, y_test=None, l1=None, disease=None, l2=None):
    from sklearn.naive_bayes import GaussianNB
    gnb = GaussianNB()
    gnb=gnb.fit(X,np.ravel(y))

    # calculating accuracy-------------------------------------------------------------------
    from sklearn.metrics import accuracy_score
    y_pred=gnb.predict(X_test)
    print(accuracy_score(y_test, y_pred))
    print(accuracy_score(y_test, y_pred,normalize=False))
    # -----------------------------------------------------

    psymptoms = [symptom1,symptom2,symptom3,symptom4,symptom5]
    for k in range(0,len(l1)):
        for z in psymptoms:
            if(z==l1[k]):
                l2[k]=1

    inputtest = [l2]
    predict = gnb.predict(inputtest)
    predicted=predict[0]
    return disease[predicted]
#     h='no'
#     for a in range(0,len(disease)):
#         if(predicted == a):
#             h='yes'
#             break
#
#     if (h=='yes'):
#         t3.delete("1.0", END)
#         t3.insert(END, disease[a])
#     else:
#         t3.delete("1.0", END)
#         t3.insert(END, "Not Found")

@app.route('/user_view_history')
def user_view_history():
    db = Db()
    qry = db.select("SELECT * FROM prediction_results WHERE user_id='"+str(session['lid'])+"'")
    pred_list = []
    for data in qry:
        pred_dict = dict()
        pred_dict["prediction_id"] = data["prediction_id"]
        pred_dict["symptoms"] = data["symptoms"]
        abc = data["predicted_disease"].split(",")
        ll = []
        for dd in abc:
            d = tuple(dd.split(":"))
            ll.append(d)
        pred_dict["prediction"] = ll
        pred_dict["date"] = data["date"]
        pred_list.append(pred_dict)
        print(pred_list)
    return render_template("user/user_view_history.html", dp_res=pred_list)

@app.route('/rm_pred_history/<i>')
def rm_pred_history(i):
    db = Db()
    qry = db.delete("DELETE FROM prediction_results WHERE prediction_id = '"+i+"'")
    return redirect('/user_view_history')

@app.route('/search_doctor')
def search_doctor():
    return render_template('user/search_doctor.html')

@app.route('/search_doctor_post', methods=['post'])
def search_doctor_post():
    opt = request.form['option']
    if opt == 'name':
        text = request.form['text']
        db = Db()
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor' AND doctor.name like '%" + text + "%'")
        return render_template('user/search_doctor.html', qry1=qry)
    elif opt == 'experience':
        db = Db()
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor' ORDER BY doctor.pro_started_yr")
        return render_template('user/search_doctor.html', qry1=qry)
    elif opt == 'location':
        db = Db()
        my_loc = db.selectOne("SELECT latitude, longitude FROM location WHERE login_id = '"+str(session['lid'])+"'")
        docs = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor'")
        return render_template('user/search_doctor.html', qry1=qry)
    elif opt == 'specialisation':
        db = Db()
        option = request.form['specialisation']
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor' AND qualification = '"+option+"'")
        return render_template('user/search_doctor.html', qry1=qry)
        return render_template('user/search_doctor.html', qry1=qry)



@app.route('/search_result')
def search_result():
    return render_template('user/search_result.html')

@app.route('/user_change_pass')
def user_change_pass():
    return render_template('user/user_change_pass.html')

@app.route('/user_send_feedback')
def user_send_feedback():
    db = Db()
    lid = session.get('lid')
    qry = db.selectOne("SELECT * FROM feedbacks WHERE user_id = '" + str(lid) + "'")
    if qry is not None:
        content = True
        return render_template('user/send_feedback.html', qry=qry, content=content)
    else:
        content = False
        return render_template('user/send_feedback.html', qry=qry, content=content)

@app.route('/send_feedback_post', methods=['post'])
def send_feedback_post():
    dates = datetime.datetime.now().strftime("%d/%m/%Y")
    rate = request.form['rate']
    review = request.form['review']
    db = Db()
    lid = session.get('lid')
    qry = db.selectOne("SELECT * FROM feedbacks WHERE user_id = '"+str(lid)+"'")
    if qry is not None:
        qry1 = db.update("UPDATE feedbacks SET rate = '" + rate + "', review = '" + review + "' WHERE user_id = '"+str(lid)+"'")
        return redirect('/user_home')
    else:
        qry1 = db.insert("INSERT INTO feedbacks VALUES('', '" + str(lid) + "', '" + rate + "', '" + review + "', '" + dates + "')")
        return redirect('/user_home')

@app.route('/search_doctor_search/<eid>')
def search_dr_experience(eid):
    if eid=='name':
        return render_template('user/search_dr/dr_name.html')
    elif eid=='specialisation':
        return render_template('user/search_dr/dr_specialisation.html')
    elif eid=='experience':
        return render_template('user/search_dr/dr_experience.html')
    elif eid=='location':
        return render_template('user/search_dr/dr_location.html')
    else:
        return render_template('user/search_doctor.html')

# @app.route('/search_doctor')
# def search_dr_experience():
#     return render_template('user/search_dr/dr_experience.html')
#
# @app.route('/search_doctor')
# def search_dr_name():
#     return render_template('user/search_dr/dr_name.html')
#
# @app.route('/search_doctor/specialisation')
# def search_dr_specialisation():
#     return render_template('user/search_dr/dr_specialisation.html')
#
# @app.route('/search_doctor/location')
# def search_dr_location():
#     return render_template('user/search_dr/dr_location.html')

########################################################################################################################

if __name__ == '__main__':
    app.run(debug=True)
