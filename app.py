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
        session['log'] = "login"
        session['lid'] = qry["login_id"]
        return redirect('/admin_home')
    elif qry is not None and qry['user_type'] == 'user':
        session['log'] = "ulogin"
        session['lid'] = qry["login_id"]
        return redirect('/user_home')
    elif qry is not None and (qry['user_type'] == 'doctor' or qry['user_type'] == 'pending'):
        session['log'] = "dlogin"
        session['lid'] = qry["login_id"]
        return redirect('/doctor_home')
    else:
        return "<script>alert('Username/Password mismatch!!'); window.location='/'</script>"

@app.route('/logout')
def logout():
    session.pop('lid', None)
    flash('You were logged out.')
    session['log'] = ""
    return redirect('/')

@app.route('/signup_post', methods=['post', 'get'])
def signup_post():
    user_type = request.form['sign-up']
    if user_type == "user":
        return redirect('/user/register')
        # return render_template('user/user_register.html')
    elif user_type == "doctor":
        return redirect('/doctor/register')
        # return render_template('doctor/doctor_register.html')

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
    db = Db()
    utype = db.selectOne("select user_type from login where login_id='"+str(session['lid'])+"'")
    if utype['user_type']=="user":
        return render_template("user/user_change_pass.html")
    elif utype['user_type']=="doctor":
        return render_template("doctor/doctor_change_pass.html")
    elif utype['user_type']=="admin":
        return render_template("admin/admin_change_pass.html")

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
    if session['log'] == "login":
        return render_template("admin/admin_base.html")
    else:
        return redirect('/')

@app.route('/dataset')
def dataset():
    if session['log'] == "login":
        db = Db()
        qry = db.select("SELECT * FROM disease_dataset")
        symptoms = []
        for i in range(len(qry)):
            symptoms.append(qry[i]["symptoms"].split(","))
        return render_template("admin/manage_dataset.html", qry=qry, symptoms=symptoms)
    else:
        return redirect('/')

@app.route('/add_dataset', methods=['post'])
def add_dataset():
    if session['log'] == "login":
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
    else:
        return redirect('/')

@app.route('/edit_dataset/<i>')
def edit_dataset(i):
    if session['log'] == "login":
        db = Db()
        qry = db.selectOne("SELECT * FROM disease_dataset WHERE dataset_id = '" + i + "'")
        return render_template('admin/dataset_edit.html', qry=qry)
    else:
        return redirect('/')

@app.route('/edit_dataset_post/<i>', methods=['post'])
def edit_dataset_post(i):
    if session['log'] == "login":
        disease_name = request.form['disease_name']
        category = request.form['category']
        symptoms = request.form['symptoms']
        count = request.form['count']
        db = Db()
        qry = db.update("UPDATE disease_dataset SET disease = '" + disease_name + "', category = '" + category + "', symptoms = '" + symptoms + "', count_of_occurrence = '" + count + "' WHERE dataset_id = '" + i + "'")
        return redirect('/dataset')
    else:
        return redirect('/')

@app.route('/doctors')
def doctors():
    if session['log'] == "login":
        db = Db()
        qry1 = db.select("SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type != 'rejected'")
        return render_template("admin/view_doctors.html", qry1=qry1)
    else:
        return redirect('/')

@app.route('/pending_dr')
def pending_dr():
    if session['log'] == "login":
        db = Db()
        qry1 = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'pending'")
        return render_template("admin/pending_dr.html", qry1=qry1)
    else:
        return redirect('/')

@app.route('/search_pending_dr', methods=['post'])
def search_pending_dr():
    if session['log'] == "login":
        text = request.form['search_pending_dr']
        db = Db()
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'pending' AND doctor.name like '%" + text + "%'")
        return render_template('admin/pending_dr.html', qry1=qry)
    else:
        return redirect('/')

@app.route('/patients')
def patients():
    if session['log'] == "login":
        db = Db()
        qry1 = db.select("SELECT * FROM user, login WHERE user.user_id = login.login_id AND login.user_type = 'user'")
        return render_template("admin/view_patients.html", qry1=qry1)
    else:
        return redirect('/')

@app.route('/search_user', methods=['POST'])
def search_user():
    if session['log'] == "login":
        text = request.form['search_patient']
        db = Db()
        qry = db.select(
            "SELECT * FROM user, login WHERE user.`user_id` = login.`login_id` AND user_type = 'user' AND user.name like '%" + text + "%'")
        return render_template('admin/view_patients.html', qry1=qry)
    else:
        return redirect('/')

@app.route('/approve_dr/<i>')
def approve_dr(i):
    if session['log'] == "login":
        db = Db()
        qry = db.update("UPDATE login SET `user_type` = 'doctor' WHERE login_id = '" + i + "'")
        return doctors()
    else:
        return redirect('/')

@app.route('/reject_dr/<i>')
def reject_dr(i):
    if session['log'] == "login":
        db = Db()
        qry = db.update("UPDATE login SET `user_type` = 'rejected' WHERE login_id = '" + i + "'")
        return doctors()
    else:
        return redirect('/')

@app.route('/search_dr', methods=['POST'])
def search_dr():
    if session['log'] == "login":
        text = request.form['search_doctor']
        db = Db()
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type != 'rejected' AND name like '%" + text + "%'")
        return render_template('admin/view_doctors.html', qry1=qry)
    else:
        return redirect('/')

@app.route('/view_more_dr/<i>')
def view_more_dr(i):
    if session['log'] == "login":
        db = Db()
        qry = db.selectOne("SELECT * FROM doctor WHERE doctor_id = '" + i + "'")
        return render_template("admin/view_more_doctor.html", qry=qry)
    else:
        return redirect('/')

@app.route('/feedbacks')
def feedbacks():
    if session['log'] == "login":
        db = Db()
        qry = db.select(
            "SELECT * FROM login, feedbacks WHERE login.login_id = feedbacks.user_id AND login.user_type='user'")
        return render_template("admin/view_feedbacks.html", qry=qry)
    else:
        return redirect('/')


############     D O C T O R     #######################################################################################

@app.route('/doctor/register')
def doctor_register():
    return render_template('doctor/doctor_register.html')

@app.route('/doctor/register_post', methods=['post'])
def doctor_register_post():
    username = request.form['username']
    name = request.form['name']
    photo = request.files['photo']
    email_address = request.form['email-address']
    contact_number = request.form['contact-number']
    gender = request.form['gender']
    dob = request.form['dob']
    license_id = request.form['license-id']
    qualification = request.form['qualification']
    category = request.form.getlist('category')
    category = ','.join(category)
    hospital_name = request.form['hospital-name']
    place = request.form['place']
    district = request.form['district']
    state = request.form['state']
    post = request.form['post']
    pin = request.form['pin']
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
                    qry) + "','" + username + "', '" + name + "', '" + path + "', '" + email_address + "', '" + contact_number + "', '" + gender + "', '" + dob + "', '" + license_id + "', '" + qualification + "', '" + category + "', '" + hospital_name + "', '" + place + "', '" + district + "', '" + state + "', '" + post + "', '" + pin + "','" + admission_fee + "', '" + pro_started_yr + "')")
            qry3 = db.insert(
                "INSERT INTO location VALUES('','" + str(qry) + "', '" + longitude + "', '" + latitude + "')")
            return redirect('/')
        else:
            return "<script>alert('Password mismatch!'); window.location='/signup_post'</script>"

@app.route('/doctor_home')
def doctor_home():

    if session['log'] == "dlogin":
        return render_template('doctor/doctor_home.html')
    else:
        return redirect('/')


@app.route('/doctor_schedule')
def doctor_schedule():
    if session['log'] == "dlogin":
        db = Db()
        qry = db.select(
            "SELECT * FROM schedule WHERE doctor_id='" + str(session['lid']) + "' ORDER BY schedule_date desc")
        return render_template('doctor/doctor_schedule.html', qry=qry)
    else:
        return redirect('/')

@app.route('/doctor_schedule_add')
def doctor_schedule_add():
    if session['log'] == "dlogin":
        return render_template('doctor/doctor_schedule_add.html')
    else:
        return redirect('/')

@app.route('/doctor_schedule_add_post', methods=['post'])
def doctor_schedule_add_post():
    if session['log'] == "dlogin":
        schedule_date = request.form['schedule_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        # schedule_date="2021-04-10"
        year, month, day = (int(x) for x in schedule_date.split('-'))
        ans = datetime.date(year, month, day)
        print(ans.strftime("%A"))
        schedule_day = ans.strftime("%A")
        db = Db()
        db.insert("INSERT INTO schedule VALUES('', '" + str(session[
                                                                'lid']) + "', '" + schedule_date + "','" + schedule_day + "', '" + start_time + "', '" + end_time + "', 'not active')")
        return doctor_schedule()
    else:
        return redirect('/')


@app.route('/doctor/schedule/rm/<i>')
def doctor_schedule_rm(i):
    if session['log'] == "dlogin":
        db = Db()
        qry = db.delete("DELETE FROM schedule WHERE schedule_id = '" + i + "'")
        return redirect('/doctor_schedule')
    else:
        return redirect('/')

@app.route('/doctor/appointment')
def doctor_appointment():
    if session['log'] == "dlogin":
        db = Db()
        qry = db.select("select * from dr_appointment where doctor_id='"+str(session['lid'])+"' and status!='Cancelled' order by schedule_date desc")


        return render_template('doctor/doctor_appointment.html', qry=qry)
    else:
        return redirect('/')

@app.route('/doctor/appointment/more/<i>')
def doctor_appointment_more(i):
    if session['log'] == "dlogin":
        db = Db()
        qry = db.selectOne("select * from dr_appointment where appointment_id='" + i + "'")
        return render_template('doctor/doctor_appointment_more.html', usr=qry)
    else:
        return redirect('/')

@app.route('/doctor/appointment/approve/<i>')
def doctor_appointment_approve(i):
    db = Db()
    db.update("UPDATE dr_appointment SET status='Booked' WHERE appointment_id='"+i+"'")
    return doctor_appointment()

@app.route('/doctor/appointment/reject/<i>')
def doctor_appointment_reject(i):
    db = Db()
    db.update("UPDATE dr_appointment SET status='Cancelled' WHERE appointment_id='"+i+"'")
    return doctor_appointment()

@app.route('/doctor/search/app-name', methods=['post'])
def doctor_search_app_name():
    text = request.form['qry-name']
    db = Db()
    qry = db.select(
        "SELECT * FROM dr_appointment WHERE doctor_id='"+str(session['lid'])+"' AND status!='Cancelled' AND patient_name like '%" + text + "%'")
    return render_template('doctor/doctor_appointment.html', qry=qry)

@app.route('/doctor/search/app-date', methods=['post'])
def doctor_search_app_date():
    date1 = request.form['date1']
    date2 = request.form['date2']
    db = Db()
    qry = db.select(
        "SELECT * FROM dr_appointment WHERE doctor_id='"+str(session['lid'])+"' AND status!='Cancelled' AND schedule_date between '"+date1+"' and '"+date2+"'")
    return render_template('doctor/doctor_appointment.html', qry=qry)

@app.route('/doctor/profile')
def doctor_profile():
    if session['log'] == "dlogin":
        db = Db()
        lid = session['lid']
        qry = db.selectOne("select * from doctor where doctor_id='" + str(lid) + "'")
        this_year = datetime.date.today().year
        age = this_year - int(qry['dob'].split('-')[0])

        return render_template("doctor/doctor_profile.html", q=qry, age=age)
    else:
        return redirect('/')

@app.route('/doctor/profile/edit')
def doctor_profile_edit():
    if session['log'] == "dlogin":
        db = Db()
        lid = session['lid']
        qry = db.selectOne("select * from doctor where doctor_id='" + str(lid) + "'")
        category = qry['category'].split(',')
        return render_template("doctor/doctor_profile_edit.html", data=qry, category=category)
    else:
        return redirect('/')

@app.route('/doctor/profile/edit/post', methods=['post'])
def doctor_profile_edit_post():
    if session['log'] == "dlogin":
        username = request.form['username']
        name = request.form['name']
        photo = request.files['photo']
        email_address = request.form['email-address']
        contact_number = request.form['contact-number']
        gender = request.form['gender']
        dob = request.form['dob']
        license_id = request.form['license-id']
        qualification = request.form['qualification']
        category = request.form.getlist('category')
        category = ','.join(category)
        hospital_name = request.form['hospital-name']
        place = request.form['place']
        district = request.form['district']
        state = request.form['state']
        post = request.form['post']
        pin = request.form['pin']
        admission_fee = request.form['admission-fee']
        pro_started_yr = request.form['pro-started-yr']

        dates = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        photo.save(path1 + dates + ".jpg")
        path = "/static/images/" + dates + ".jpg"
        db = Db()
        if request.files is not None:
            if photo.filename != "":
                qry = db.update(
                    "UPDATE doctor SET username='" + username + "',name='" + name + "', photo='" + path + "', email_address='" + email_address + "', contact_number='" + contact_number + "', gender='" + gender + "', dob='" + dob + "', license_id='" + license_id + "', qualification='" + qualification + "', category='" + category + "', hospital_name='" + hospital_name + "', place='" + place + "', district='" + district + "', state='" + state + "', post='" + post + "', pin='" + pin + "', admission_fee='" + admission_fee + "', pro_started_yr='" + pro_started_yr + "' WHERE doctor_id='" + str(
                        session['lid']) + "'")
            else:
                qry = db.update(
                    "UPDATE doctor SET username='" + username + "',name='" + name + "', email_address='" + email_address + "', contact_number='" + contact_number + "', gender='" + gender + "', dob='" + dob + "', license_id='" + license_id + "', qualification='" + qualification + "', category='" + category + "', hospital_name='" + hospital_name + "', place='" + place + "', district='" + district + "', state='" + state + "', post='" + post + "', pin='" + pin + "', admission_fee='" + admission_fee + "', pro_started_yr='" + pro_started_yr + "' WHERE doctor_id='" + str(
                        session['lid']) + "'")
        else:
            qry = db.update(
                    "UPDATE doctor SET username='" + username + "',name='" + name + "', email_address='" + email_address + "', contact_number='" + contact_number + "', gender='" + gender + "', dob='" + dob + "', license_id='" + license_id + "', qualification='" + qualification + "', category='" + category + "', hospital_name='" + hospital_name + "', place='" + place + "', district='" + district + "', state='" + state + "', post='" + post + "', pin='" + pin + "', admission_fee='" + admission_fee + "', pro_started_yr='" + pro_started_yr + "' WHERE doctor_id='" + str(
                        session['lid']) + "'")
        return doctor_profile()
    else:
        return redirect('/')


############     U S E R     ###########################################################################################

@app.route("/user/register")
def user_register():
    return render_template("user/user_register.html")

@app.route('/user/register_post', methods=['post'])
def user_register_post():
    username = request.form['username']
    name = request.form['name']
    photo = request.files['photo']
    email_address = request.form['email-address']
    mobile_number = request.form['mobile-number']
    gender = request.form['gender']
    dob = request.form['dob']
    house_name = request.form['house-name']
    place = request.form['place']
    district = request.form['district']
    state = request.form['state']
    post = request.form['post']
    pin = request.form['pin']
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
        return "<script>alert('Username already exist!'); window.location='/user/register'</script>"
    else:
        if password == re_password:
            qry = db.insert("INSERT INTO login VALUES('','" + username + "', '" + password + "', 'user')")
            qry1 = db.insert(
                "INSERT INTO user VALUES('" + str(
                    qry) + "','" + username + "', '" + name + "', '" + path + "', '" + email_address + "', '" + mobile_number + "', '" + gender + "', '" + dob + "', '" + house_name + "', '" + place + "', '" + district + "', '" + state + "', '" + post + "', '" + pin + "')")

            qry3 = db.insert("INSERT INTO location VALUES('','" + str(qry) + "', '"+longitude+"', '"+latitude+"')")
            return redirect('/')
        else:
            return "<script>alert('Password mismatch!'); window.location='/user/register'</script>"

@app.route('/user_home')
def user_home():

    if session['log'] == "ulogin":
        return render_template("user/user_home.html")
    else:
        return redirect('/')

@app.route('/user/profile')
def user_profile():
    if session['log'] == "ulogin":
        db = Db()
        lid = session['lid']
        qry = db.selectOne("select * from user where user_id='" + str(lid) + "'")
        this_year = datetime.date.today().year
        age = this_year - int(qry['dob'].split('-')[0])
        return render_template("user/user_profile.html", q=qry, age=age)
    else:
        return redirect('/')

@app.route('/user/profile/edit')
def user_profile_edit():
    if session['log'] == "ulogin":
        db = Db()
        lid = session['lid']
        qry = db.selectOne("select * from user where user_id='" + str(lid) + "'")
        return render_template("user/user_profile_edit.html", data=qry)
    else:
        return redirect('/')

@app.route('/user/profile/edit-post',methods=['post'])
def user_profile_edit_post():
    if session['log'] == "ulogin":
        username = request.form['username']
        name = request.form['name']
        photo = request.files['photo']
        email_address = request.form['email-address']
        mobile_number = request.form['mobile-number']
        gender = request.form['gender']
        dob = request.form['dob']
        house_name = request.form['house-name']
        place = request.form['place']
        district = request.form['district']
        state = request.form['state']
        post = request.form['post']
        pin = request.form['pin']
        dates = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        photo.save(path1 + dates + ".jpg")
        path = "/static/images/" + dates + ".jpg"
        db = Db()
        if request.files is not None:
            if photo.filename != "":
                qry = db.update(
                    "UPDATE login, user SET login.username='" + username + "',user.username='" + username + "',user.name='" + name + "', user.photo='" + path + "', user.email_address='" + email_address + "',user.mobile_number='" + mobile_number + "', user.gender='" + gender + "', user.dob='" + dob + "', user.house_name='" + house_name + "', user.place='" + place + "', user.district='" + district + "',user.state='" + state + "', user.post='" + post + "', user.pin='" + pin + "' WHERE login.login_id = user.user_id AND login.login_id='" + str(
                        session.get('lid')) + "'")
            else:
                qry = db.update(
                    "UPDATE login, user SET login.username='" + username + "',user.username='" + username + "',user.name='" + name + "', user.email_address='" + email_address + "',user.mobile_number='" + mobile_number + "', user.gender='" + gender + "', user.dob='" + dob + "', user.house_name='" + house_name + "', user.place='" + place + "', user.district='" + district + "',user.state='" + state + "', user.post='" + post + "', user.pin='" + pin + "' WHERE login.login_id = user.user_id AND login.login_id='" + str(
                        session.get('lid')) + "'")
        else:
            qry = db.update(
                "UPDATE login, user SET login.username='" + username + "',user.username='" + username + "',user.name='" + name + "', user.email_address='" + email_address + "',user.mobile_number='" + mobile_number + "', user.gender='" + gender + "', user.dob='" + dob + "', user.house_name='" + house_name + "', user.place='" + place + "', user.district='" + district + "',user.state='" + state + "', user.post='" + post + "', user.pin='" + pin + "' WHERE login.login_id = user.user_id AND login.login_id='" + str(
                    session.get('lid')) + "'")
        return user_profile()
    else:
        return redirect('/')

@app.route('/nearestservice',methods=['get'])
def nearestservice():
    if session['log'] == "ulogin":
        db = Db()
        user_loc = db.selectOne("SELECT * FROM location WHERE location.login_id = '" + str(session['lid']) + "'")
        # doc_loc = db.select("SELECT * FROM login, location WHERE location.login_id = login.login_id AND login.user_type = 'doctor'")
        # print(doc_loc)
        print(user_loc)
        qry = db.select("SELECT  (3959 * ACOS ( COS ( RADIANS('" + str(user_loc[
                                                                           'latitude']) + "') ) * COS( RADIANS( location.latitude) ) * COS( RADIANS( location.longitude ) - RADIANS('" + str(
            user_loc['longitude']) + "') ) + SIN ( RADIANS('" + str(user_loc[
                                                                        'latitude']) + "') ) * SIN( RADIANS(  location.latitude ) ))) AS user_distance,doctor.* FROM doctor, login, location WHERE doctor.doctor_id = login.login_id AND location.login_id = login.login_id AND login.user_type = 'doctor' HAVING user_distance  < 100000.2137")
        print(qry)
        return "ok"
    else:
        return redirect('/')


@app.route('/user/add_symptoms')
def user_add_symptoms():
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
    return render_template('user/user_add_symtoms.html', l1=l1)

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

# @app.route('/user/add_symptoms_post', methods=['post'])
# def user_add_symptoms_post():
#     symptoms1 = request.form['symptoms1']
#     symptoms2 = request.form['symptoms2']
#     symptoms3 = request.form['symptoms3']
#     symptoms4 = request.form['symptoms4']
#     symptoms5 = request.form['symptoms5']
#     session['symptoms'] = [symptoms1, symptoms2, symptoms3, symptoms4, symptoms5]
#     return redirect('/user/disease_prediction')


@app.route('/user/disease_prediction', methods=['post'])
def user_disease_prediction():
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
    #     return render_template("user/user_disease_predictions.html", res1="False", qry=symptoms)

    # sym_valid = [True for sym in symptoms if sym in l1]
    # print(sym_valid)


    res1=DecisionTree(symptoms[0], symptoms[1], symptoms[2], symptoms[3], symptoms[4], X, y, X_test, y_test, l1, disease, l2)
    res2=randomforest(symptoms[0], symptoms[1], symptoms[2], symptoms[3], symptoms[4], X, y, X_test, y_test, l1, disease, l2)
    res3=NaiveBayes(symptoms[0], symptoms[1], symptoms[2], symptoms[3], symptoms[4], X, y, X_test, y_test, l1, disease, l2)

    syms = f"{symptoms[0]},{symptoms[1]},{symptoms[2]},{symptoms[3]},{symptoms[4]}"
    syms = syms.rstrip(',')
    algo = ["Decision Tree", "Random Forest", "Naive Bayes"]

    res1 = res1.strip()
    res2 = res2.strip()
    res3 = res3.strip()

    predictions = f"{algo[0]}:{res1},{algo[1]}:{res2},{algo[2]}:{res3}"
    #print(predictions)
    #print(type(predictions))

    db = Db()

    # Dr Recommendation Algorithm

    disease_category = {
                'Fungal infection': 'Dermatologist',
                'Allergy': 'Allergist',
                'GERD': 'Gastroenterologist',
                'Chronic cholestasis': ['Gastroenterologist', 'Hepatologist'],
                'Drug Reaction': 'Allergist',
                'Peptic ulcer diseae': 'Gastroenterologist',
                'AIDS': ['Internist', 'Osteopaths'],
                'Diabetes': ['Diabetologist', 'Endocrinologist'],
                'Gastroenteritis': 'Gastroenterologist',
                'Bronchial Asthma': ['Pulmonologist', 'Allergist'],
                'Hypertension': ['Cardiologist', 'Psychologist'],
                'Migraine': 'Neurologist',
                'Cervical spondylosis': ['Neurologist', 'Orthopedic Specialist'],
                'Paralysis (brain hemorrhage)': 'Neurologist',
                'Jaundice': 'Gastroenterologist',
                'Malaria': 'General Physician',
                'Chicken pox': 'General Physician',
                'Dengue': 'General Physician',
                'Typhoid': 'General Physician',
                'hepatitis A': ['Gastroenterologist', 'Hepatologist'],
                'Hepatitis B': ['Gastroenterologist', 'Hepatologist'],
                'Hepatitis C': ['Gastroenterologist', 'Hepatologist'],
                'Hepatitis D': ['Gastroenterologist', 'Hepatologist'],
                'Hepatitis E': ['Gastroenterologist', 'Hepatologist'],
                'Alcoholic hepatitis': ['Gastroenterologist', 'Hepatologist'],
                'Tuberculosis': ['General Physician', 'Pulmonologist'],
                'Common Cold': 'General Physician',
                'Pneumonia': ['General Physician', 'Pulmonologist'],
                'Dimorphic hemmorhoids(piles)': ['Gastroenterologist', 'Surgeon'],
                'Heart attack': 'Cardiologist',
                'Varicose veins': ['Vascular Surgeon', 'Dermatologist'],
                'Hypothyroidism': 'Endocrinologist',
                'Hyperthyroidism': 'Endocrinologist',
                'Hypoglycemia': 'Endocrinologist',
                'Osteoarthristis': 'Orthopedic Specialist',
                'Arthritis': 'Orthopedic Specialist',
                '(vertigo) Paroymsal  Positional Vertigo': 'ENT',
                'Acne': 'Dermatologist',
                'Urinary tract infection': 'Urologist',
                'Psoriasis': 'Dermatologist',
                'Impetigo': 'Dermatologist'
    }

    recommended_category = []
    if isinstance(disease_category[res1], list):
        recommended_category.extend(disease_category[res1])
    elif isinstance(disease_category[res1], str):
        recommended_category.append(disease_category[res1])

    if isinstance(disease_category[res2], list):
        recommended_category.extend(disease_category[res2])
    elif isinstance(disease_category[res2], str):
        recommended_category.append(disease_category[res2])

    if isinstance(disease_category[res3], list):
        recommended_category.extend(disease_category[res3])
    elif isinstance(disease_category[res3], str):
        recommended_category.append(disease_category[res3])

    if len(recommended_category) == 0:
        recommended_category.append('General Physician')

    lid = session['lid']
    qry5 = db.selectOne("select * from user where user_id='" + str(lid) + "'")
    this_year = datetime.date.today().year
    age = this_year - int(qry5['dob'].split('-')[0])

    if age < 18:
        recommended_category.append('Paediatrician')

    recommended_category = set(recommended_category)
    recommended_category = list(recommended_category)

    print(recommended_category)

    dates = datetime.datetime.now().strftime("%Y-%m-%d.%H:%M:%S")

    if 'Paediatrician' in recommended_category:
        qry2 = db.select(
            "select * from doctor, login where login.login_id=doctor.doctor_id and login.user_type='doctor' and doctor.category like '%" + 'Paediatrician' + "%'")
    else:
        qry2 = []
        for category in recommended_category:
            drs = db.select(
                "select * from doctor, login where login.login_id=doctor.doctor_id and login.user_type='doctor' and doctor.category like '%" + category + "%'")
            qry2.extend(drs)


    qry3 = []
    for i in range(len(qry2)):
        if qry2[i] not in qry2[i + 1:]:
            qry3.append(qry2[i])

    import random
    random.shuffle(qry3)

    qry2 = qry3

    if len(qry2) > 5:
        qry2 = qry2[0:5]

    # drs = ""
    # for x in qry2:
    #     drs += str(x['doctor_id']) + ','
    # drs = drs.rstrip(',')
    # print(drs)


    dp_row = db.insert("INSERT INTO prediction_results VALUES('','" + str(session['lid']) + "', '" + syms + "', '" + predictions + "', '"+dates+"')")
    # qry1 = db.select("SELECT * FROM login, doctor WHERE login.login_id=doctor.doctor_id AND login.user_type='doctor'")

    for x in qry2:
        db.insert("INSERT INTO dr_recommendation VALUES('','" + str(dp_row) + "', '" + str(x['doctor_id']) + "', '" + x['category'] + "')")


    return render_template("user/user_disease_predictions.html", res1=res1, res2=res2, res3=res3, qry=symptoms, qry1=qry2, l=[len(qry2)])




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

@app.route('/user/dp_history')
def user_dp_history():
    db = Db()
    qry = db.select("SELECT * FROM prediction_results WHERE user_id='"+str(session['lid'])+"' order by date desc")
    pred_list = []
    for data in qry:
        pred_dict = dict()
        pred_dict["prediction_id"] = data["prediction_id"]
        sym_set = list(filter(lambda x: x != "", data["symptoms"].split(',')))
        pred_dict["symptoms"] = sym_set
        # sym_set1 = ", ".join(sym_set1)
        # sym_set1 = sym_set1.strip()
        abc = data["predicted_disease"].split(",")
        ll = []
        for dd in abc:
            d = tuple(dd.split(":"))
            ll.append(d)
        pred_dict["prediction"] = ll
        pred_dict["date"] = data["date"].split(".")
        pred_list.append(pred_dict)
    return render_template("user/user_dp_history.html", dp_res=pred_list)

@app.route('/user/dp_history/dr_rec/<i>')
def user_dp_history_dr_rec(i):
    db = Db()
    qry = db.select("SELECT * FROM dr_recommendation, doctor WHERE dr_recommendation.doctor_id=doctor.doctor_id and dr_recommendation.prediction_id='"+i+"'")
    session['pd_id'] = int(i)
    return render_template("user/user_dp_history_dr_rec.html", qry1=qry, l=[len(qry)])

@app.route('/user/dr/appointment/<i>')
def user_dr_appointment(i):
    session['did'] = int(i)
    db = Db()
    today = str(datetime.date.today())
    qry = db.select("select * from user, prediction_results where  user.user_id=prediction_results.user_id and prediction_results.prediction_id='"+str(session['pd_id'])+"'")
    xlist = qry[0]['predicted_disease'].split(',')
    pred = []
    for x in xlist:
        pred.append([x.split(':')[0], x.split(':')[1]])
    this_year = datetime.date.today().year
    age = this_year - int(qry[0]['dob'].split('-')[0])
    today_date = str(datetime.date.today())

    qry2 = db.selectOne(
        "select * from doctor, login where  doctor.doctor_id=login.login_id and login.user_type='doctor' and doctor.doctor_id='"+str(i)+"'")

    qry3 = db.select("select * from schedule where doctor_id='" + str(i) + "' and schedule_date >= '" + today + "'")
    print(i)
    print(qry3)
    return render_template('user/user_dr_appointment.html', usr=qry, pred=pred, age=age, dr=qry2, app=qry3)


@app.route('/user/my_appointment')
def user_my_appointment():
    db = Db()
    qry = db.select("select * from dr_appointment where user_id='"+str(session['lid'])+"'")
    return render_template('user/user_myappointment.html', qry=qry)

@app.route('/user/dp_history/rm/<i>')
def user_dp_history_rm(i):
    db = Db()
    qry = db.delete("DELETE FROM prediction_results WHERE prediction_id = '"+i+"'")
    return redirect('/user/dp_history')

@app.route('/search_doctor')
def search_doctor():
    return render_template('user/search_doctor.html', l=[0])

@app.route('/search_doctor_post', methods=['post'])
def search_doctor_post():
    opt = request.form['option']
    if opt == 'name':
        text = request.form['text']
        db = Db()
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor' AND doctor.name like '%" + text + "%'")
        return render_template('user/search_doctor.html', qry1=qry, l=[len(qry)])
    elif opt == 'experience':
        db = Db()
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor' ORDER BY doctor.pro_started_yr")
        return render_template('user/search_doctor.html', qry1=qry, l=[len(qry)])
    elif opt == 'location':
        #my_loc = db.selectOne("SELECT latitude, longitude FROM location WHERE login_id = '"+str(session['lid'])+"'")
        #docs = db.select(
        #    "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor'")

        db = Db()
        user_loc = db.selectOne("SELECT * FROM location WHERE location.login_id = '" + str(session['lid']) + "'")
        # doc_loc = db.select("SELECT * FROM login, location WHERE location.login_id = login.login_id AND login.user_type = 'doctor'")
        # print(doc_loc)
        print(user_loc)
        qry = db.select("SELECT  (3959 * ACOS ( COS ( RADIANS('" + str(user_loc[
                                                                           'latitude']) + "') ) * COS( RADIANS( location.latitude) ) * COS( RADIANS( location.longitude ) - RADIANS('" + str(
            user_loc['longitude']) + "') ) + SIN ( RADIANS('" + str(user_loc[
                                                                        'latitude']) + "') ) * SIN( RADIANS(  location.latitude ) ))) AS user_distance,doctor.* FROM doctor, login, location WHERE doctor.doctor_id = login.login_id AND location.login_id = login.login_id AND login.user_type = 'doctor' HAVING user_distance  < 100000.2137 order by user_distance asc")

        return render_template('user/search_doctor.html', qry1=qry, l=[len(qry)])
    elif opt == 'specialisation':
        db = Db()
        option = request.form['specialisation']
        qry = db.select(
            "SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type = 'doctor' AND qualification = '"+option+"'")
        return render_template('user/search_doctor.html', qry1=qry, l=[len(qry)])
    elif opt == "select":
        return search_doctor()



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

@app.route('/search_dr_experience/<eid>')
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

@app.route('/user/appointment/submit', methods=['post'])
def user_appointment_submit():
    patient_name = request.form['patient-name']
    patient_age = request.form['patient-age']
    patient_address = request.form['patient-address']
    patient_email = request.form['patient-email']
    patient_mobile = request.form['patient-mobile']
    dr_name = request.form['dr-name']
    dr_address = request.form['dr-address']
    option_date = request.form['option-date']
    option_time = request.form['option-time']

    symptoms = request.form['symptoms']
    prediction1 = request.form['prediction1']
    prediction2 = request.form['prediction2']
    prediction3 = request.form['prediction3']
    prediction_date = request.form['prediction-date']
    pred_id = request.form['pred-id']
    dr_id = request.form['dr-id']
    patient_username = request.form['patient-username']

    db = Db()
    shdl = db.selectOne("select * from schedule where doctor_id='"+dr_id+"' and schedule_date='"+option_date+"' and start_time='"+option_time.split('-')[0]+"' and end_time='"+option_time.split('-')[1]+"'")

    qry = db.insert("INSERT INTO dr_appointment VALUES('', '"+pred_id+"', '"+dr_id+"', '"+str(session['lid'])+"', '"+str(shdl['schedule_id'])+"', '"+patient_name+"', '"+patient_username+"', '"+patient_age+"', '"+patient_address+"', '"+patient_email+"', '"+patient_mobile+"', '"+shdl['schedule_date']+"', '"+shdl['schedule_day']+"', '"+shdl['start_time']+"', '"+shdl['end_time']+"', '"+symptoms+"', '"+prediction1+"', '"+prediction2+"', '"+prediction3+"', '"+prediction_date+"', 'Pending')")


    return  'ok'


########################### -------------------------
@app.route('/appointment_select/<eid>')
def appointment_select(eid):
    db = Db()
    today = str(datetime.date.today())
    i = session['did']
    qry = db.select(
        "select * from user, prediction_results where  user.user_id=prediction_results.user_id and prediction_results.prediction_id='" + str(
            session['pd_id']) + "'")
    xlist = qry[0]['predicted_disease'].split(',')
    pred = []
    for x in xlist:
        pred.append([x.split(':')[0], x.split(':')[1]])
    this_year = datetime.date.today().year
    age = this_year - int(qry[0]['dob'].split('-')[0])
    today_date = str(datetime.date.today())

    qry2 = db.selectOne(
        "select * from doctor, login where  doctor.doctor_id=login.login_id and login.user_type='doctor' and doctor.doctor_id='" + str(
            i) + "'")

    qry3 = db.select("select * from schedule where doctor_id='" + str(i) + "' and schedule_date >= '"+today+"'")

    app_dates = db.select("select schedule_date from schedule where doctor_id='" + str(i) + "' and schedule_date >= '"+today+"'")
    app_dates = [x['schedule_date'] for x in app_dates]
    print(app_dates)
    print(eid)
    if eid in app_dates:
        times = db.select("select start_time, end_time from schedule where doctor_id='" + str(i) + "' and schedule_date='"+eid+"'")
        print(times)
        return render_template('user/user_dr_appointment_time.html', times=times, eid=eid)
    else:
        print('else')
        return render_template('user/user_dr_appointment_time.html',  usr=qry, pred=pred, age=age, dr=qry2, app=qry3)

# @app.route('/appointment_select_post', methods=['post'])
# def appointment_select_post():
#     return render_template("user/user_dr_appointment.html")

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
