from flask import Flask, render_template, request, redirect
from DBConnection import Db

app = Flask(__name__)


@app.route('/')
def login():
    return render_template("login.html")


@app.route('/login_post', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    db = Db()
    qry = db.selectOne("SELECT * FROM login WHERE username='"+username+"' AND PASSWORD='"+password+"'")
    if qry is not None:
        return redirect('/admin_home')
    else:
        return "<script>alert('Username/Password mismatch!!'); window.location='/'</script>"

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

if __name__ == '__main__':
    app.run(debug=True)
