from flask import Flask, render_template, request, redirect
from DBConnection import Db
from email.mime import image
import os, datetime
from flask import Flask, render_template, request, redirect,session
import smtplib
from email.mime.text import MIMEText
from flask_mail import Mail
from random import randint

app = Flask(__name__)
app.secret_key="kmsoe89j42"

path1=r"C:\Users\user\Documents\PROGRAMS\PycharmProjects\DiseasePredictionApp\static\images\\"
path2=r'C:\Users\user\Documents\PROGRAMS\PycharmProjects\dp_notes\dp_notes.txt'

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login_post', methods=['POST'])
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
# ====================================================================================================================

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
    qry = db.selectOne("select * from user where user_id='" + str(lid) + "'")
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
            qry=db.update("UPDATE `user` SET `username`='"+username+"',`email_address`='"+email+"',`name`='"+name+"'`photo`='"+path+"',`home`='"+home+"',`date_of_birth`='"+date_of_birth+"',`mobile_number`='"+phone_number+"',`place`='"+place+"',`pin`='"+pin+"',`post`='"+post+"' WHERE `user_id`='"+str(session['lid'])+"'")
        else:
            qry = db.update(
                "UPDATE `user` SET `username`='" + username + "',`email_address`='"+email+"',`name`='"+name+"',`home`='"+home+"',`date_of_birth`='"+date_of_birth+"',`mobile_number`='"+phone_number+"',`place`='"+place+"',`pin`='"+pin+"',`post`='"+post+"' WHERE `user_id`='"+str(session['lid'])+"'")
    else:
            qry = db.update(
                "UPDATE `user` SET `username`='" + username + "',`email_address`='"+email+"',`name`='"+name+"',`home`='"+home+"',`date_of_birth`='"+date_of_birth+"',`mobile_number`='"+phone_number+"',`place`='"+place+"',`pin`='"+pin+"',`post`='"+post+"' WHERE `user_id`='"+str(session['lid'])+"'")
    return view_user_profile()
	
# =================================================================================================================

@app.route('/add_symptoms')
def add_symptoms():
    return render_template('user/add_symtoms.html')

@app.route('/disease_prediction_result')
def disease_prediction_result():
    return render_template('user/disease_prediction_result.html')

@app.route('/search_doctor')
def search_doctor():
    return render_template('user/search_doctor.html')

@app.route('/user_change_pass')
def user_change_pass():
    return render_template('user/user_change_pass.html')

@app.route('/user_view_history')
def user_view_history():
    return render_template('user/user_view_history.html')

@app.route('/user_send_feedback')
def user_send_feedback():
    return render_template('user/send_feedback.html')


if __name__ == '__main__':
    app.run(debug=True)
