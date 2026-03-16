from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="student_db"
)

cursor = db.cursor()

@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/dashboard')

    return render_template("login.html")
@app.route('/dashboard')
def dashboard():

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance WHERE status='Present'")
    present = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance WHERE status='Absent'")
    absent = cursor.fetchone()[0]

    if total_attendance > 0:
        attendance_percent = round((present/total_attendance)*100,2)
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
@app.route('/add_student', methods=['GET','POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        reg = request.form['reg']
        dept = request.form['dept']
        year = request.form['year']
        email = request.form['email']

        sql = "INSERT INTO students (name,reg_no,department,year,email) VALUES (%s,%s,%s,%s,%s)"
        val = (name,reg,dept,year,email)

        cursor.execute(sql,val)
        db.commit()

        return redirect('/students')

    return render_template('add_student.html')

@app.route('/students')
def students():
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    return render_template('students.html', students=data)
@app.route('/delete/<int:id>')
def delete_student(id):

    sql = "DELETE FROM students WHERE id=%s"
    val = (id,)

    cursor.execute(sql,val)
    db.commit()

    return redirect('/students')
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit_student(id):

    if request.method == 'POST':

        name = request.form['name']
        reg = request.form['reg']
        dept = request.form['dept']
        year = request.form['year']
        email = request.form['email']

        sql = """UPDATE students 
                 SET name=%s, reg_no=%s, department=%s, year=%s, email=%s 
                 WHERE id=%s"""

        val = (name,reg,dept,year,email,id)

        cursor.execute(sql,val)
        db.commit()

        return redirect('/students')

    sql = "SELECT * FROM students WHERE id=%s"
    val = (id,)

    cursor.execute(sql,val)

    student = cursor.fetchone()

    return render_template("edit_student.html",student=student)

@app.route('/attendance', methods=['GET','POST'])
def attendance():

    if request.method == 'POST':
        student_id = request.form['student_id']
        date = request.form['date']
        status = request.form['status']

        sql = "INSERT INTO attendance (student_id,date,status) VALUES (%s,%s,%s)"
        val = (student_id,date,status)

        cursor.execute(sql,val)
        db.commit()

        return redirect('/attendance')

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    return render_template("attendance.html", students=students)
@app.route('/view_attendance')
def view_attendance():

    sql = """
    SELECT students.name, students.reg_no, attendance.date, attendance.status
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    """

    cursor.execute(sql)

    data = cursor.fetchall()

    return render_template("view_attendance.html", records=data)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)