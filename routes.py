from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from models.models import Student, Admin, Course
import barcode
from barcode.writer import ImageWriter
from datetime import datetime
import random
import os

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@main.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    if user_type == 'student':
        registration_number = request.form.get('registration_number')
        user = Student.query.filter_by(registration_number=registration_number).first()
    elif user_type == 'admin':
        email = request.form.get('email')
        user = Admin.query.filter_by(email=email).first()

    if user and user.password == password:
        session['user_id'] = user.id
        session['user_type'] = user_type
        if user_type == 'student':
            return redirect(url_for('main.student_dashboard'))
        elif user_type == 'admin':
            return redirect(url_for('main.admin_dashboard'))
    else:
        flash('Login failed! Check your credentials and try again.')
        return redirect(url_for('main.home'))

@main.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    if 'user_id' in session and session.get('user_type') == 'student':
        return render_template("student_dashboard.html")
    else:
        return redirect(url_for('main.home'))

@main.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'user_id' in session and session.get('user_type') == 'admin':
        admin = Admin.query.filter_by(id=session['user_id']).first()
        courses = Course.get_all()
        return render_template("admin_dashboard.html", admin=admin, courses=courses)
    else:
        return redirect(url_for('main.home'))

@main.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('main.home'))

@main.route('/admin_update', methods=['POST'])
def admin_update():
    if 'user_id' in session and session.get('user_type') == 'admin':
        email = request.form.get('email')
        password = request.form.get('password')
        admin = Admin.query.filter_by(id=session['user_id']).first()

        if email:
            admin.email = email
        if password:
            admin.password = password

        try:
            admin.save()
            flash('Account updated successfully!')
        except:
            flash('Update failed. Please try again.')

        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.home'))

@main.route('/admin_create_course', methods=['POST'])
def admin_create_course():
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

@main.route('/admin_create_student', methods=['POST'])
def admin_create_student():
    if 'user_id' in session and session.get('user_type') == 'admin':
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        course_acronym = request.form.get('course_acronym')

        # Generate the registration number
        current_year = datetime.now().year
        random_number = random.randint(1000, 9999)
        registration_number = f"{course_acronym}/{current_year}/{random_number}"

        if not name or not phone_number or not password or not course_acronym:
            flash('Please fill in all the fields.')
            return redirect(url_for('main.admin_dashboard'))

        course = Course.query.filter_by(acronym=course_acronym).first()
        if not course:
            flash('Invalid course acronym.')
            return redirect(url_for('main.admin_dashboard'))

        student = Student(name=name, phone_number=phone_number, registration_number=registration_number, password=password, course_acronym=course_acronym)

        # Create the directory if it doesn't exist
        barcode_dir = 'static/barcodes'
        if not os.path.exists(barcode_dir):
            os.makedirs(barcode_dir)

        # Generate barcode
        barcode_writer = ImageWriter()
        barcode_obj = barcode.get('code128', registration_number, writer=barcode_writer)
        barcode_path = os.path.join(barcode_dir, f'{registration_number.replace("/","_")}.png')
        barcode_obj.save(barcode_path)

        student.save()
        flash('Student created successfully!')
        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.home'))
