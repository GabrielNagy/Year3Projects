#!/usr/bin/env python
import datetime
import couchdbkit
from couchdbkit import Document, StringProperty, DateTimeProperty
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_recaptcha import ReCaptcha
import logging
import os
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import uuid
from celery import Celery
import subprocess
from shutil import copy2


DATABASE = 'upload_app'
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

UPLOAD_FOLDER = 'static/uploads'
SOURCE_FOLDER = 'run/src'
BUILD_FOLDER = 'run/build'
ALLOWED_EXTENSIONS = set(['cc', 'c', 'h', 'cpp'])

basedir = os.path.abspath(os.path.dirname(__file__))

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


@app.route('/static/uploads/<path:path>')
def uploads(path):
    if session.get('logged_in'):
        files = g.db.view("users/by_uploads", key=session.get('username'), id=path)
        if files.first() or session.get('is_admin'):
            for file in files:
                if path in file['id']:
                    return send_from_directory(os.path.join('.', 'static', 'uploads'), path, as_attachment=True, attachment_filename=file['value'])
    flash("You are not authorized to view this file", 'danger')
    return redirect(url_for('status'))


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
    if ('file-source' or 'file-header') not in request.files:
        flash('Missing header or source file', 'danger')
        return redirect(url_for('status'))
    headerfile = request.files['file-header']
    sourcefile = request.files['file-source']
    if headerfile.filename == '' or sourcefile.filename == '':
        flash('Missing header or source file', 'danger')
        return redirect(url_for('status'))
    if (headerfile and allowed_file(headerfile.filename)) and (sourcefile and allowed_file(sourcefile.filename)):
        headerfilename = secure_filename(headerfile.filename)
        sourcefilename = secure_filename(sourcefile.filename)
        unique_id = str(uuid.uuid4())
        headerSavedFilename = unique_id + '.h'
        sourceSavedFilename = unique_id + '.cc'
        headerfile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], headerSavedFilename))
        sourcefile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], sourceSavedFilename))
        entry = Entry(
            _id=unique_id,
            author=session.get('username'),
            original_header=headerfilename,
            original_source=sourcefilename,
            date=datetime.datetime.utcnow())
        g.db.save_doc(entry)
        flash('Your files were successfully uploaded.', 'success')
        return redirect(url_for('status'))
    flash('Invalid extension', 'danger')
    return redirect(url_for('status'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were successfully logged out', 'success')
    return redirect(url_for('status'))


@app.route('/delete/<path:path>')
def delete_file(path):
    if session.get('logged_in'):
        files = g.db.view("users/by_uploads", key=session.get('username'), id=path)
        if files.first() or session.get('is_admin'):
            for file in files:
                if path in file['id']:
                    fileToRemove = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
                    os.remove(fileToRemove + '.cc')
                    os.remove(fileToRemove + '.h')
                    g.db.delete_doc(path)
                    flash("File successfully removed.", 'success')
                    return redirect(url_for('status'))
    flash("You are not authorized to do this.", 'danger')
    return redirect(url_for('status'))


@celery.task(bind=True)
def run_task(self, path):
    unique_path = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
    sourcefile = unique_path + '.cc'
    headerfile = unique_path + '.h'
    copy2(sourcefile, os.path.join(basedir, app.config['SOURCE_FOLDER'], 'templateSrc.cc'))
    copy2(headerfile, os.path.join(basedir, app.config['SOURCE_FOLDER'], 'templateSrc.h'))
    p = subprocess.Popen(['cmake .. && make && make check'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.join(basedir, app.config['BUILD_FOLDER']), shell=True)
    stdout = []
    while True:
        line = p.stdout.readline()
        stdout.append(line)
        self.update_state(state='PROGRESS', meta={'status': stdout})
        if line == '' and p.poll() is not None:
            break
    return {'status': stdout,
            'result': 'Task completed!'}


@app.route('/run/<path:path>', methods=['POST'])
def runtask(path):
    run_task.apply_async(args=[path], task_id=path)
    return jsonify({}), 202, {'Location': url_for('taskstatus', path=path)}


@app.route('/status/<path:path>')
def taskstatus(path):
    task = run_task.AsyncResult(path)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': []
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


app.debug = True
app.logger.setLevel(logging.INFO)
couchdbkit.set_logging('info')

if __name__ == "__main__":
    app.run()
