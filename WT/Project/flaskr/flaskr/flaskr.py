#!/usr/bin/env python
import datetime
import couchdbkit
from couchdbkit import Document, StringProperty, DateTimeProperty
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_bcrypt import Bcrypt
from flask_recaptcha import ReCaptcha
import logging
import os
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, PasswordField, validators

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

UPLOAD_FOLDER = 'flaskr/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'cpp', 'c', 'py', 'html', 'js'])

app = Flask(__name__)
app.config.from_object(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
recaptcha = ReCaptcha(app=app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def connect_db():
    server = couchdbkit.Server("http://admin:admin@127.0.0.1:5984")
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


class File(Document):
    author = StringProperty()
    date = DateTimeProperty()
    title = StringProperty()
    text = StringProperty()
    filename = StringProperty()


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address')
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=4, max=50)
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()
    File.set_db(g.db)
    # User.set_db(g.db)


@app.teardown_request
def teardown_request(exception):
    """Closes the database at the end of the request."""


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(username=request.form['username'], email=request.form['email'],
                    password=bcrypt.generate_password_hash(request.form['password']),
                    date=datetime.datetime.utcnow())
        g.db.save_doc(user)
        flash('Thanks for registering')
        return redirect(url_for('register'))
    return render_template('status.html', form=form, success="Thanks for registering! You can now log in.")


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
                    session['username'] = user['key']
                    flash('You were successfully logged in')
                    return redirect(url_for('status'))
        else:
            error = 'Please complete captcha'
    return render_template('login.html', error=error)


@app.route('/add', methods=['POST'])
def add_entry():
    # error = None
    if not session.get('logged_in'):
        abort(401)
    app.logger.debug('before entry added')
    if 'file' not in request.files:
        return render_template('status.html', error='No file selected')
        # return redirect(url_for('status'))

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return render_template('status.html', error='No file selected')
        # return redirect(url_for('status'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        error = 'Extension has to be one of '
        for extension in app.config['ALLOWED_EXTENSIONS']:
            error += extension + ', '
        return render_template('status.html', error=error)
    entry = File(
        author='test',
        title=request.form['title'],
        text=request.form['text'],
        filename=filename,
        date=datetime.datetime.utcnow())
    g.db.save_doc(entry)
    app.logger.debug('after entry added')
    flash('New entry was successfully posted')
    return redirect('status.html')


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file', filename=filename))
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <p><input type=file name=file>
        <input type=submit value=Upload>
        </form>
    '''


@app.route('/')
def status():
    # using a view (NOTE: you will have to create the appropriate view in CouchDB)
    # entries = g.db.view('entry/all', schema=Entry)
    # using the primary index _all_docs
    # entries = g.db.all_docs(include_docs=True, schema=Entry)
    # classes={None: <document class>}
    # app.logger.debug(entries.all())
    return render_template('status.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were successfully logged out')
    return redirect(url_for('status'))


app.debug = True
app.logger.setLevel(logging.INFO)

couchdbkit.set_logging('info')

if __name__ == "__main__":
    app.run()
