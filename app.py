import json
import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

STUDENT_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"


# --------------------------
# JSON FUNCTIONS
# --------------------------

def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)


def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


# --------------------------
# LOGIN
# --------------------------

@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/dashboard')

    return render_template("login.html")


# --------------------------
# DASHBOARD
# --------------------------

@app.route('/dashboard')
def dashboard():

    students = load_data(STUDENT_FILE)
    attendance = load_data(ATTENDANCE_FILE)

    total_students = len(students)
    total_attendance = len(attendance)

    present = sum(1 for a in attendance if a["status"] == "Present")
    absent = sum(1 for a in attendance if a["status"] == "Absent")

    if total_attendance > 0:
        attendance_percent = round((present / total_attendance) * 100, 2)
    else:
        attendance_percent = 0

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_attendance=total_attendance,
        attendance_percent=attendance_percent,
        present=present,
        absent=absent
    )


# --------------------------
# ADD STUDENT
# --------------------------

@app.route('/add_student', methods=['GET','POST'])
def add_student():

    if request.method == 'POST':

        students = load_data(STUDENT_FILE)

        new_student = {
            "id": len(students) + 1,
            "name": request.form['name'],
            "reg_no": request.form['reg'],
            "department": request.form['dept'],
            "year": request.form['year'],
            "email": request.form['email']
        }

        students.append(new_student)

        save_data(STUDENT_FILE, students)

        return redirect('/students')

    return render_template('add_student.html')


# --------------------------
# VIEW STUDENTS
# --------------------------

@app.route('/students')
def students():

    students = load_data(STUDENT_FILE)

    return render_template('students.html', students=students)


# --------------------------
# DELETE STUDENT
# --------------------------

@app.route('/delete/<int:id>')
def delete_student(id):

    students = load_data(STUDENT_FILE)

    students = [s for s in students if s["id"] != id]

    save_data(STUDENT_FILE, students)

    return redirect('/students')


# --------------------------
# EDIT STUDENT
# --------------------------

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit_student(id):

    students = load_data(STUDENT_FILE)

    student = next((s for s in students if s["id"] == id), None)

    if request.method == 'POST':

        student["name"] = request.form['name']
        student["reg_no"] = request.form['reg']
        student["department"] = request.form['dept']
        student["year"] = request.form['year']
        student["email"] = request.form['email']

        save_data(STUDENT_FILE, students)

        return redirect('/students')

    return render_template("edit_student.html", student=student)


# --------------------------
# MARK ATTENDANCE
# --------------------------

@app.route('/attendance', methods=['GET','POST'])
def attendance():

    students = load_data(STUDENT_FILE)

    if request.method == 'POST':

        attendance = load_data(ATTENDANCE_FILE)

        new_record = {
            "student_id": request.form['student_id'],
            "date": request.form['date'],
            "status": request.form['status']
        }

        attendance.append(new_record)

        save_data(ATTENDANCE_FILE, attendance)

        return redirect('/view_attendance')

    return render_template("attendance.html", students=students)


# --------------------------
# VIEW ATTENDANCE
# --------------------------

@app.route('/view_attendance')
def view_attendance():

    students = load_data(STUDENT_FILE)
    attendance = load_data(ATTENDANCE_FILE)

    records = []

    for a in attendance:
        for s in students:
            if str(s["id"]) == str(a["student_id"]):
                records.append({
                    "name": s["name"],
                    "reg_no": s["reg_no"],
                    "date": a["date"],
                    "status": a["status"]
                })

    return render_template("view_attendance.html", records=records)


# --------------------------
# RUN SERVER
# --------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)