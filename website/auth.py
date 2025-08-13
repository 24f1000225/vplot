from flask import Blueprint, render_template, redirect, request, flash, url_for
from .models import db, User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 

auth = Blueprint('auth', __name__)

#signup route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')


        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists")
            return redirect('/signup')

        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect('/user_dashboard')

    return render_template('signup.html')

# login route 
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", category='success')
            if user.is_admin:
                flash("Welcome Admin!", category='info')
                return redirect(url_for('views.admin_dashboard'))
            else:
                flash(f"Welcome {current_user.name}! ", category='info')
                return redirect(url_for('views.user_dashboard'))
        else:
            flash("Invalid credentials. Please try again.", category='error')

    return render_template("login.html")


# logout route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))