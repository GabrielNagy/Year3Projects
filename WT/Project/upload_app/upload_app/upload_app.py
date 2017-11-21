#!/usr/bin/env python
import datetime
import couchdbkit
from couchdbkit import Document, StringProperty, DateTimeProperty
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup
from flask_bcrypt import Bcrypt
from flask_recaptcha import ReCaptcha
import logging
import os
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import uuid
from celery import Celery


DATABASE = 'flaskr'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'admin'
RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = "6LcqfTkUAAAAABorDOh3Ex1fgOKoeDxC9_n9yCi8"
RECAPTCHA_SECRET_KEY = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J"
RECAPTCHA_THEME = "light"
RECAPTCHA_TYPE = "image"
RECAPTCHA_SIZE = "normal"
RECAPTCHA_RTABINDEX = 10
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

UPLOAD_FOLDER = 'upload_app/static/uploads'
ALLOWED_EXTENSIONS = set(['sh', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'cpp', 'c', 'py', 'html', 'js'])

app = Flask(__name__)
app.config.from_object(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
recaptcha = ReCaptcha(app=app)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text, error), 'danger')


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def connect_db():
    server = couchdbkit.Server()
    return server.get_or_create_db(app.config['DATABASE'])


def init_db():
    db = connect_db()
    loader = couchdbkit.loaders.FileSystemDocsLoader('_design')
    loader.sync(db, verbose=True)


class User(Document):
    username = StringProperty()
    email = StringProperty()
    password = StringProperty()
    date = DateTimeProperty()


class Entry(Document):
    author = StringProperty()
    date = DateTimeProperty()
    original = StringProperty()


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Email()])
    password = PasswordField('Password', [
        validators.Length(min=4),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('TOS', [validators.DataRequired()])


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()
    Entry.set_db(g.db)


@app.teardown_request
def teardown_request(exception):
    """Closes the database at the end of the request."""


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        check_user = g.db.view("users/by_username", key=request.form['username'])
        check_email = g.db.view("users/by_email", key=request.form['email'])
        if check_user.first():
            flash("An user with this name already exists.", 'danger')
            return redirect(url_for('register'))
        if check_email.first():
            flash(Markup("An user with this email already exists. <a href='/login'>Login</a> if you already have an account."), 'danger')
            return redirect(url_for('register'))
        user = User(username=request.form['username'], email=request.form['email'],
                    password=bcrypt.generate_password_hash(request.form['password']),
                    date=datetime.datetime.utcnow())
        g.db.save_doc(user)
        flash(Markup('Thanks for registering! You can now <a href="/login">login</a>.'), 'success')
        return redirect(url_for('status'))
    else:
        flash_errors(form)
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not recaptcha.verify():
            result = g.db.view("users/by_username", key=request.form['username'])
            if result.first() is None:
                error = 'Invalid username'
            else:
                user = result.first()
                if not bcrypt.check_password_hash(user['value'], request.form['password']):
                    error = 'Invalid credentials'
                else:
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash('You were successfully logged in', 'success')
                    return redirect(url_for('status'))
        else:
            error = 'Please complete captcha'
    return render_template('login.html', error=error)


@app.route('/')
def status():
    # using a view (NOTE: you will have to create the appropriate view in CouchDB)
    # entries = g.db.view('entry/all', schema=Entry)
    # using the primary index _all_docs
    # entries = g.db.all_docs(include_docs=True, schema=Entry)
    # app.logger.debug(entries.all())
    files = None
    if session.get('logged_in'):
        files = g.db.view("users/by_uploads", key=session.get('username'))
    return render_template('status.html', files=files)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    app.logger.debug('before entry added')
    if 'file' not in request.files:
        flash('No selected file', 'danger')
        return redirect(url_for('status'))
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('status'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        savedFilename = str(uuid.uuid4())
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], savedFilename))
        entry = Entry(
            _id=savedFilename,
            author=session.get('username'),
            original=filename,
            date=datetime.datetime.utcnow())
        g.db.save_doc(entry)
        app.logger.debug('after entry added')
        flash('New entry was successfully posted', 'success')
        return redirect(url_for('status'))
    flash('Invalid extension', 'danger')
    return redirect(url_for('status'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were successfully logged out', 'success')
    return redirect(url_for('status'))


app.debug = True
app.logger.setLevel(logging.INFO)
couchdbkit.set_logging('info')

if __name__ == "__main__":
    app.run()
