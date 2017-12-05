#!/usr/bin/env python
# from extensions import RequestContextTask
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
from shutil import copy2, copytree, rmtree
import glob
import filecmp
from timeit import timeit
import errno


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
if "COUCHDB_USER" and "COUCHDB_PASS" in os.environ:
    COUCHDB_URL = 'http://%s:%s@127.0.0.1:5984' % (os.getenv("COUCHDB_USER"), os.getenv("COUCHDB_PASS"))
else:
    COUCHDB_URL = 'http://admin:admin@127.0.0.1:5984'

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
    server = couchdbkit.Server(app.config['COUCHDB_URL'])
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
    User.set_db(g.db)


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


# @app.route('/add', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     # if ('file-source' or 'file-header') not in request.files:
#     if 'file-source' not in request.files:
#         flash('Missing source file', 'danger')
#         return redirect(url_for('status'))
#     # headerfile = request.files['file-header']
#     sourcefile = request.files['file-source']
#     # if 'file-header' in request.files:
#         # headerfile = request.files['file-header'
#     # if headerfile.filename == '' or sourcefile.filename == '':
#     if sourcefile.filename == '':
#         flash('Missing header or source file', 'danger')
#         return redirect(url_for('status'))
#     # if (headerfile and allowed_file(headerfile.filename)) and (sourcefile and allowed_file(sourcefile.filename)):
#     if sourcefile and allowed_file(sourcefile.filename):
#         # headerfilename = secure_filename(headerfile.filename)
#         sourcefilename = secure_filename(sourcefile.filename)
#         unique_id = str(uuid.uuid4())
#         # headerSavedFilename = unique_id + '.h'
#         sourceSavedFilename = unique_id + '.cc'
#         # headerfile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], headerSavedFilename))
#         sourcefile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], sourceSavedFilename))
#         entry = Entry(
#             _id=unique_id,
#             author=session.get('username'),
#             original_header=headerfilename or 'None',
#             original_source=sourcefilename,
#             date=datetime.datetime.utcnow())
#         g.db.save_doc(entry)
#         flash('Your files were successfully uploaded.', 'success')
#         return redirect(url_for('status'))
#     flash('Invalid extension', 'danger')
#     return redirect(url_for('status'))


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    if 'file-source' not in request.files:
        flash('Missing source file', 'danger')
        return redirect(url_for('status'))
    sourcefile = request.files['file-source']
    if 'file-header' in request.files and request.form.get:
        # headerfile = request.files['file-header'
    # if headerfile.filename == '' or sourcefile.filename == '':
    if sourcefile.filename == '':
        flash('Missing header or source file', 'danger')
        return redirect(url_for('status'))
    # if (headerfile and allowed_file(headerfile.filename)) and (sourcefile and allowed_file(sourcefile.filename)):
    if sourcefile and allowed_file(sourcefile.filename):
        # headerfilename = secure_filename(headerfile.filename)
        sourcefilename = secure_filename(sourcefile.filename)
        unique_id = str(uuid.uuid4())
        # headerSavedFilename = unique_id + '.h'
        sourceSavedFilename = unique_id + '.cc'
        # headerfile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], headerSavedFilename))
        sourcefile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], sourceSavedFilename))
        entry = Entry(
            _id=unique_id,
            author=session.get('username'),
            original_header=headerfilename or 'None',
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


@app.route('/rankings')
def generate_rankings():
    rankings = g.db.view("users/by_duration")
    if rankings.first():
        return render_template('rankings.html', rankings=rankings)
    flash("There are no rankings available yet", 'danger')
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


def store_duration(path, stdout):
    for row in stdout:
        if "Total Test time" in row:
            if '=' in row:
                server = couchdbkit.Server(app.config['COUCHDB_URL'])
                db = server.get_or_create_db(app.config['DATABASE'])
                doc = db.get(path)
                if 'duration' not in doc:
                    key, value = row.split('=')
                    doc['duration'] = float(value.strip('sec').split()[0])
                    db.save_doc(doc)
                    return True


@celery.task(bind=True)
def run_task_old(self, path):
    if os.path.exists(os.path.join(basedir, path)):
        rmtree(os.path.join(basedir, path))
    copytree(os.path.join(basedir, 'run'), os.path.join(basedir, path))
    unique_path = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
    sourcefile = unique_path + '.cc'
    headerfile = unique_path + '.h'
    copy2(sourcefile, os.path.join(basedir, path, 'templateSrc.cc'))
    copy2(headerfile, os.path.join(basedir, path, 'templateSrc.h'))
    p = subprocess.Popen(['cmake .. && make && make check'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.join(basedir, path, 'build'), shell=True)
    stdout = []
    while True:
        line = p.stdout.readline()
        stdout.append(line)
        self.update_state(state='PROGRESS', meta={'status': stdout})
        if line == '' and p.poll() is not None:
            break
    rmtree(os.path.join(basedir, path))
    store_duration(path, stdout)
    return {'status': stdout,
            'result': 'Task completed!'}


def number_of_tests(problem):
    return len([name for name in os.listdir('%s/tests/%s' % (basedir, problem)) if os.path.isfile(os.path.join(basedir, 'tests', problem, name))]) / 2


def run_tests(path, problem, test_count):
    results = []
    total = 0
    working_directory = basedir + '/' + path
    for test in range(1, test_count + 1):
        for file_path in glob.glob(r'%s/tests/%s/grader_test%d.*' % (basedir, problem, test)):
            filename, extension = file_path.split('.')
            dest_file = problem + '.' + extension
            copy2(file_path, os.path.join(basedir, path, dest_file))
        time_elapsed = timeit(stmt="subprocess.check_output('./%s;exit 0', shell=True, cwd='%s', stderr=subprocess.STDOUT)" % (problem, working_directory), setup="import subprocess", number=1)
        # time_elapsed = timeit(stmt="subprocess.check_output('./%s', cwd='%s', stderr=subprocess.STDOUT)" % (problem, working_directory), setup="import subprocess", number=1)
        if filecmp.cmp('%s/%s/%s.out' % (basedir, path, problem), '%s/%s/%s.ok' % (basedir, path, problem)):
            results.append('PASSED in {0:.3f}\n'.format(time_elapsed))
            total += time_elapsed
        else:
            results.append('FAILED')
    results.append(round(total, 3))
    return results


@celery.task(bind=True)
def run_task(self, path):
    if os.path.exists(os.path.join(basedir, path)):
        rmtree(os.path.join(basedir, path))
    unique_path = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
    sourcefile = unique_path + '.cc'
    # headerfile = unique_path + '.h'
    try:
        copy2(sourcefile, os.path.join(basedir, path, 'templateSrc.cc'))
    except IOError as e:
        # ENOENT(2): file does not exist, raised also on missing dest parent dir
        if e.errno != errno.ENOENT:
            raise
        # try creating parent directories
        os.makedirs(os.path.join(basedir, path))
        copy2(sourcefile, os.path.join(basedir, path, 'templateSrc.cc'))
    copy2(sourcefile, os.path.join(basedir, path, 'templateSrc.cc'))
    # if os.path.isfile(headerfile):
    #     copy2(headerfile, os.path.join(basedir, path, 'templateSrc.h'))
    subprocess.check_call(['g++', 'templateSrc.cc', '-I.', '-o', 'kfib'], cwd=os.path.join(basedir, path))
    stdout = run_tests(path, 'kfib', number_of_tests('kfib'))
    rmtree(os.path.join(basedir, path))
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
