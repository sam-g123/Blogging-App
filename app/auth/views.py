from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, current_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm
from ..emails import send_email
import logging
from datetime import datetime

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('Auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data,
                    name=form.username.data,
                    location=form.location.data,
                    member_since=datetime.utcnow())  
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                    'Auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('Auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        logging.debug(f'User {current_user.email} already confirmed')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
        logging.debug(f'User {current_user.email} confirmed successfully')
    else:
        flash('The confirmation link is invalid or has expired.')
        logging.debug(f'User {current_user.email} failed to confirm with token {token}')
    return redirect(url_for('auth.after_confirm'))

@auth.route('/after_confirm')
@login_required
def after_confirm():
    return render_template('auth/after_confirm.html')

# Prevent unconfirmed users from accessing the user's page 
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('Auth/email/unconfirmed.html', user=current_user)


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    try:
        send_email(current_user.email, 'Confirm Your Account',
                   'Auth/email/confirm', user=current_user, token=token)
        flash('A new confirmation email has been sent to your email address.')
    except Exception as e:
        current_app.logger.error(f'Error resending confirmation email: {e}')
        flash('An error occurred while sending the confirmation email. Please try again later.')
    return redirect(url_for('main.index'))