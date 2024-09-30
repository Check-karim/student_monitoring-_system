import qrcode
from flask import Blueprint, jsonify, render_template, request, flash, session, redirect, url_for
from models.models import Student, Admin, Course
import os
from datetime import datetime
import random
from extensions import db
import subprocess

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@main.route('/getStarted', methods=['GET'])
def getStarted():
    return render_template("login-register.html")

@main.route('/login', methods=['POST'])
def login():
    try:
        password = request.form.get('password')
        email = request.form.get('email')
        user = Admin.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Login failed! Check your credentials and try again.')
            return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"An error occurred during login: {str(e)}")
        return redirect(url_for('main.home'))


@main.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    # Get the student_id from the query parameters
    student_id = request.args.get('student_id')

    # Check if student_id is provided
    if student_id is None:
        flash("Student ID is missing. Redirecting to the Login.")
        return redirect(url_for('main.login'))
    student = Student.query.filter_by(id=student_id).first()
    # Render the student dashboard if everything is okay
    return render_template("student_dashboard.html", student=student)

@main.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    try:
        if 'user_id' in session:
            admin = Admin.query.filter_by(id=session['user_id']).first()
            courses = Course.get_all()
            students = Student.query.all()
            return render_template("admin_dashboard.html", students=students, admin=admin, courses=courses)
        else:
            return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"An error occurred while loading the admin dashboard: {str(e)}")
        return redirect(url_for('main.home'))

@main.route('/logout', methods=['GET'])
def logout():
    try:
        session.clear()
        return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"An error occurred during logout: {str(e)}")
        return redirect(url_for('main.home'))

@main.route('/admin_update', methods=['POST'])
def admin_update():
    try:
        if 'user_id' in session and session.get('user_type') == 'admin':
            email = request.form.get('email')
            password = request.form.get('password')
            admin = Admin.query.filter_by(id=session['user_id']).first()

            if email:
                admin.email = email
            if password:
                admin.password = password

            admin.save()
            flash('Account updated successfully!')
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"An error occurred during account update: {str(e)}")
        return redirect(url_for('main.admin_dashboard'))

@main.route('/admin_create_course', methods=['POST'])
def admin_create_course():
    try:
        if 'user_id' in session and session.get('user_type') == 'admin':
            name = request.form.get('name')
            acronym = request.form.get('acronym')

            if not name or not acronym:
                flash('Please provide both course name and acronym.')
                return redirect(url_for('main.admin_dashboard'))

            course = Course(name=name, acronym=acronym)
            course.save()
            flash('Course created successfully!')
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"An error occurred while creating the course: {str(e)}")
        return redirect(url_for('main.admin_dashboard'))

@main.route('/admin_create_student', methods=['POST'])
def admin_create_student():
    try:
        if 'user_id':
            name = request.form.get('name')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            dob = request.form.get('dob')
            course_acronym = request.form.get('course_acronym')

            # Generate the registration number
            current_year = datetime.now().year
            random_number = random.randint(1000, 9999)
            registration_number = f"{course_acronym}/{current_year}/{random_number}"

            if not name or not phone_number or not email or not dob or not course_acronym:
                flash('Please fill in all the fields.')
                return redirect(url_for('main.admin_dashboard'))

            course = Course.query.filter_by(acronym=course_acronym).first()
            if not course:
                flash('Invalid course acronym.')
                return redirect(url_for('main.admin_dashboard'))

            student = Student(name=name, phone_number=phone_number, registration_number=registration_number, dob=dob, email=email, course_acronym=course_acronym)

            # Define the directory to store the QR codes
            qr_code_dir = 'static/qrcodes'
            if not os.path.exists(qr_code_dir):
                os.makedirs(qr_code_dir)

            # Generate a QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(registration_number)
            qr.make(fit=True)

            # Create an image from the QR code
            img = qr.make_image(fill='black', back_color='white')

            # Define the file path and save the QR code as a PNG
            qr_code_path = os.path.join(qr_code_dir, f'{registration_number.replace("/", "_")}.png')
            img.save(qr_code_path)

            student.save()
            flash('Student created successfully!')
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"An error occurred while creating the student: {str(e)}")
        return redirect(url_for('main.admin_dashboard'))

@main.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    try:
        if 'user_id' in session and session.get('user_type') == 'admin':
            student = Student.query.filter_by(id=student_id).first()
            return render_template('edit_student.html', student=student)
    except Exception as e:
        flash(f"An error occurred while updating the student: {str(e)}")
        return redirect(url_for('main.admin_dashboard'))

@main.route('/save_edit_student/<int:student_id>', methods=['GET', 'POST'])
def save_edit_student(student_id):
    try:
        if 'user_id' in session and session.get('user_type') == 'admin':
            student = Student.query.filter_by(id=student_id).first()

            name = request.form.get('name')
            dob = request.form.get('dob')
            email = request.form.get('email')

            if name:
                student.name = name
            if dob:
                student.dob = dob
            if email:
                student.email = email

            student.save()
            flash('Student updated successfully!')
            return redirect(url_for('main.admin_dashboard'))
    except Exception as e:
        flash(f"An error occurred while updating the student: {str(e)}")
        return redirect(url_for('main.admin_dashboard'))

@main.route('/delete_student/<int:student_id>', methods=['GET'])
def delete_student(student_id):
    try:
        if 'user_id' in session:
            student = Student.query.filter_by(id=student_id).first()
            if student:
                db.session.delete(student)
                db.session.commit()
                flash('Student deleted successfully!')
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"An error occurred while deleting the student: {str(e)}")
        return redirect(url_for('main.admin_dashboard'))


@main.route('/barcode_login', methods=['POST'])
def barcode_login():
    data = request.get_json()
    barcode = data.get('barcode')
    print(barcode)

    if not barcode:
        flash('No barcode data received')
        return jsonify({"success": False, "message": "No barcode data received"})

    try:
        # Example: Searching for a student by barcode in the database
        student = Student.query.filter_by(
            registration_number=barcode).first()  # Assuming 'barcode' is a field in your Student model

        if student:
            # If the student is found, create the redirect URL for the student dashboard
            student_id = student.id  # Assuming the student model has an 'id' attribute
            redirect_url = url_for('main.student_dashboard', student_id=student_id, _external=True)
            return jsonify({"success": True, "redirect_url": redirect_url})
        else:
            return jsonify({"success": False, "message": "Student not found"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing the request: {str(e)}"})