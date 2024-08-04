from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from models.models import Student, Admin

main = Blueprint('main', __name__)  # routename= main

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
        return render_template("admin_dashboard.html", admin=admin)
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

