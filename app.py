from flask import Flask, render_template, request, redirect
from DBConnection import Db
from email.mime import image
import os
from flask import Flask, render_template, request, redirect,session
import smtplib
from email.mime.text import MIMEText
from flask_mail import Mail
from random import randint



app = Flask(__name__)
app.secret_key="kmsoe89j42"

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login_post', methods=['POST', 'GET'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    btn = request.form['login']
    db = Db()
    qry = db.selectOne("SELECT * FROM login WHERE username='"+username+"' AND password ='"+password+"'")
    if qry is not None and qry['user_type'] == 'admin':
        session['lid'] = qry["login_id"]
        return redirect('/admin_home')
    elif qry is not None and qry['user_type'] == 'user':
        session['lid'] = qry["login_id"]
        return redirect('/user_home')
    else:
        return "<script>alert('Username/Password mismatch!!'); window.location='/'</script>"

@app.route('/login_post2', methods=['POST', 'GET'])
def login_post2():
    username = request.form['username']
    print(username)
    return "ok"


@app.route("/signup")
def signup():
    pass



@app.route('/admin_home')
def admin_home():
    return render_template("admin/admin_home.html")

@app.route('/dataset')
def dataset():
    db = Db()
    qry = db.select("SELECT * FROM disease_dataset")
    print(qry)
    symptoms = []
    for i in range(len(qry)):
        symptoms.append(qry[i]["symptoms"].split(","))
    print(symptoms)
    return render_template("admin/manage_dataset.html", qry=qry, symptoms=symptoms)

@app.route("/forgot_password")
def forgot_password():

    try:
        gmail = smtplib.SMTP('smtp.gmail.com', 587)

        gmail.ehlo()

        gmail.starttls()

        with open('path') as f:
            my_email = f.writelines()
            my_email_password = f.writelines()
            gmail.login(my_email, my_email_password)

    except Exception as e:
        print("Couldn't setup email!!" + str(e))

    otpvalue = randint(1000, 9999)

    msg = MIMEText("Your OTP is " + otpvalue)

    msg['Subject'] = 'Verification'

    email = "aswanth.kizh@gmail.com"

    msg['To'] = email

    msg['From'] = 'vvrr2731@gmail.com'

    try:

        gmail.send_message(msg)

    except Exception as e:

        print("COULDN'T SEND EMAIL", str(e))

    session['otp'] = otpvalue

    return render_template("/forgot_password.html")

@app.route("/forgot_password_post", methods=["POST"])
def forgot_password_post():
    username = request.form['recovery-email']
    db = Db()
    qry = db.selectOne("SELECT * FROM login, user, doctor WHERE user.user_id = username='" + username + "'")
    if qry is not None:
        return redirect('/admin_home')
    else:
        return "<script>alert('Username/Password mismatch!!'); window.location='/'</script>"

@app.route("/reset_password")
def reset_password():
    email = request.form['recovery-email']
    return render_template("/reset_password")

@app.route('/admin_change_pass')
def admin_change_pass():
    return render_template("admin/admin_change_pass.html")

@app.route('/admin_change_pass_post', methods=['POST'])
def admin_change_pass_post():
    current_pass = request.form['current-pass']
    new_pass = request.form['new-password']
    re_new_pass = request.form['re-new-password']
    db = Db()
    lid = session.get('lid')
    qry = db.selectOne("SELECT * FROM login WHERE login_id = '"+str(lid)+"'")
    if qry is not None:
        if qry["password"] == current_pass:
            if new_pass == re_new_pass:
                qry = db.update("UPDATE login SET password = '"+new_pass+"' WHERE login_id = '"+str(session['lid'])+"'")
                return "<script>alert('Succesfully Changed'); window.location='/'</script>"
            else:
                return "<script>alert('New password mismatch!!'); window.location='/'</script>"
        else:
            return "<script>alert('Incorrect old password!!'); window.location='/'</script>"


@app.route('/doctors')
def doctors():
    db = Db()
    qry1 = db.select("SELECT * FROM doctor, login WHERE doctor.`doctor_id` = login.`login_id` AND user_type != 'rejected'")
    return render_template("admin/view_doctors.html", qry1=qry1)




@app.route('/user_home')
def user_home():
    return render_template("user/user_home.html")















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
    qry = db.select("SELECT * FROM user, feedbacks WHERE user.user_id = feedbacks.user_id")
    return render_template("admin/view_feedbacks.html", qry=qry)

if __name__ == '__main__':
    app.run(debug=True)
