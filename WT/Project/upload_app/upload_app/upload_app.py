#!/usr/bin/env python
# from extensions import RequestContextTask
import datetime
import couchdbkit
from couchdbkit import Document, StringProperty, DateTimeProperty
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
# from flask_recaptcha import ReCaptcha
import logging
import os
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators
import uuid
from celery import Celery
import subprocess
from shutil import copy2, rmtree
import glob
from timeit import timeit
from itertools import izip


DATABASE = 'upload_app'
DEBUG = True
SECRET_KEY = 'development key'
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
ALLOWED_EXTENSIONS = set(['cc', 'c', 'h', 'cpp', 'pas', 'java', 'c++', 'hh', 'hpp', 'h++'])

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
# recaptcha = ReCaptcha(app=app)


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


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Email()])
    password = PasswordField('Password', [
        validators.Length(min=4),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    grade = SelectField('Grade', [validators.DataRequired()], choices=[('elev', 'elev'), ('student', 'student')])
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
                    grade=request.form['grade'], date=datetime.datetime.utcnow())
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
        # if not recaptcha.verify():
        result = g.db.view("users/by_username", key=request.form['username'])
        if result.first() is None:
            error = 'Invalid username'
        else:
            user = result.first()
            if not bcrypt.check_password_hash(user['value'][0], request.form['password']):
                error = 'Invalid credentials'
            else:
                session['logged_in'] = True
                session['username'] = request.form['username']
                session['grade'] = user['value'][1]
                if user['value'][2]:
                    session['admin'] = user['value'][2]
                flash('You were successfully logged in', 'success')
                return redirect(url_for('status'))
        # else:
            # error = 'Please complete captcha'
    return render_template('login.html', error=error)


@app.route('/static/uploads/<path:path>')
def uploads(path):
    if session.get('logged_in'):
        files = g.db.view("users/by_uploads", key=session.get('username'))
        if files.first() or session.get('is_admin'):
            for file in files:
                if path in file['id']:
                    path = path + '.' + file['value'][2]
                    return send_from_directory(os.path.join('.', 'static', 'uploads'), path, as_attachment=True, attachment_filename=file['value'][0])
    flash("You are not authorized to view this file", 'danger')
    return redirect(url_for('status'))


@app.route('/')
def status():
    files = None
    if session.get('logged_in'):
        if session.get('admin'):
            files = g.db.view("users/by_uploads")
        else:
            files = g.db.view("users/by_uploads", key=session.get('username'))
    return render_template('status.html', files=files)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    if 'file-source' not in request.files:
        flash('Missing source file', 'danger')
        return redirect(url_for('status'))
    if request.files['file-source'].filename == '':
        flash('Missing source file', 'danger')
        return redirect(url_for('status'))
    existing = g.db.view("users/by_existing", key=[session.get('username'), request.form['problem']])
    if existing.first():
        flash('You can only upload one of each problem at a time', 'danger')
        return redirect(url_for('status'))
    sourcefile = request.files['file-source']
    if request.files['file-header'].filename and request.form['language'] not in ['c', 'cpp']:
        flash('Header file only available for C and C++', 'danger')
        return redirect(url_for('status'))
    else:
        headerfile = request.files['file-header']
    if sourcefile and allowed_file(sourcefile.filename):
        unique_id = str(uuid.uuid4())
        if headerfile and allowed_file(headerfile.filename):
            headerfilename = secure_filename(headerfile.filename)
            headerSavedFilename = unique_id + '.h'
            headerfile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], headerSavedFilename))
        else:
            headerfilename = None
        sourcefilename = secure_filename(sourcefile.filename)
        if request.form['language'] == 'c':
            sourceSavedFilename = unique_id + '.c'
        elif request.form['language'] == 'cpp':
            sourceSavedFilename = unique_id + '.cpp'
        elif request.form['language'] == 'pas':
            sourceSavedFilename = unique_id + '.pas'
        elif request.form['language'] == 'java':
            sourceSavedFilename = unique_id + '.java'
        sourcefile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], sourceSavedFilename))
        entry = Entry(
            _id=unique_id,
            author=session.get('username'),
            original_source=sourcefilename,
            language=request.form['language'],
            problem=request.form['problem'],
            grade=session.get('grade'),
            date=datetime.datetime.utcnow())
        if headerfilename is not None:
            entry['original_header'] = headerfilename
        g.db.save_doc(entry)
        flash('Your problem was successfully uploaded.', 'success')
        return redirect(url_for('status'))
    flash('Invalid extension', 'danger')
    return redirect(url_for('status'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('grade', None)
    session.pop('admin', None)
    flash('You were successfully logged out', 'success')
    return redirect(url_for('status'))


@app.route('/rankings/<problem>')
def generate_specific_rankings(problem):
    grade = session.get('grade')
    if problem not in ['kfib', 'dijkstra']:
        flash("Invalid problem name", 'danger')
        return redirect(url_for('status'))
    rankings = g.db.view('users/by_results', startkey=["%s" % problem, "%s" % grade], endkey=["%s" % problem, "%s" % grade, {}])
    if rankings.first():
        return render_template('rankings.html', rankings=rankings)
    flash("No rankings available for that problem yet", 'danger')
    return redirect(url_for('generate_rankings'))


@app.route('/rankings')
def generate_rankings():
    grade = session.get('grade')
    if not grade:
        abort(401)
    rankings = g.db.list("users/by_total", "users/by_total", group="true", group_level=2)
    if rankings:
        for entry in rankings:
            if entry['grade'] != grade and not session.get('admin'):
                rankings.remove(entry)
        return render_template('rankings.html', rankings=rankings)
    flash("There are no rankings available yet", 'danger')
    return redirect(url_for('status'))


@app.route('/delete/<path:path>')
def delete_file(path):
    if session.get('logged_in'):
        if session.get('admin'):
            files = g.db.view("users/by_uploads")
        else:
            files = g.db.view("users/by_uploads", key=session.get('username'))
        if files.first() or session.get('admin'):
            for file in files:
                if path in file['id']:
                    fileToRemove = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
                    for f in glob.glob('%s*' % fileToRemove):
                        os.remove(f)
                    g.db.delete_doc(path)
                    flash("File successfully removed.", 'success')
                    return redirect(url_for('status'))
    flash("You are not authorized to do this.", 'danger')
    return redirect(url_for('status'))


def store_duration(path, stdout, failed=None):
    server = couchdbkit.Server(app.config['COUCHDB_URL'])
    db = server.get_or_create_db(app.config['DATABASE'])
    doc = db.get(path)
    if failed is None:
        concat = ''.join(stdout)
        total = float(stdout[-1].split(',')[0].strip('Total: '))
        points = int(stdout[-2].split(':')[1].strip())
        if 'tested' not in doc:
            doc['total'] = total
            doc['failed'] = failed
            doc['points'] = points * -1
            doc['stdout'] = concat
            doc['tested'] = 1
    else:
        # for row in stdout.split('\n'):
        #     if 'Points' in row:
        #         points = row.split(': ')[1]
        doc['stdout'] = stdout
        # doc['points'] = int(points)
        doc['tested'] = 2
    db.save_doc(doc)
    return True


def number_of_tests(problem, grade):
    return len([name for name in os.listdir('%s/tests/%s' % (basedir, problem)) if name.startswith(grade) and os.path.isfile(os.path.join(basedir, 'tests', problem, name))]) / 2


def compare_files(fpath1, fpath2):
    with open(fpath1, 'r') as file1, open(fpath2, 'r') as file2:
        for linef1, linef2 in izip(file1, file2):
            linef1 = linef1.rstrip('\r\n')
            linef2 = linef2.rstrip('\r\n')
            if linef1 != linef2:
                return False
        return next(file1, None) is None and next(file2, None) is None


def run_tests(path, problem, language, grade, test_count):
    results = []
    total = 0
    failed = 0
    working_directory = basedir + '/' + path
    for test in range(1, test_count + 1):
        for file_path in glob.glob(r'%s/tests/%s/%s-test%d.*' % (basedir, problem, grade, test)):
            filename, extension = file_path.split('.')
            dest_file = problem + '.' + extension
            copy2(file_path, os.path.join(basedir, path, dest_file))
        if language == 'java':
            time_elapsed = timeit(stmt="subprocess.check_output('java Main;exit 0', shell=True, cwd='%s', stderr=subprocess.STDOUT)" % working_directory, setup="import subprocess", number=3) / 3
        else:
            time_elapsed = timeit(stmt="subprocess.check_output('./%s;exit 0', shell=True, cwd='%s', stderr=subprocess.STDOUT)" % (problem, working_directory), setup="import subprocess", number=3) / 3
        if compare_files('%s/%s/%s.out' % (basedir, path, problem), '%s/%s/%s.ok' % (basedir, path, problem)):
            results.append('Test {:d} PASSED in {:.3f} seconds\n'.format(test, time_elapsed))
            total += time_elapsed
        else:
            results.append('Test {:d} FAILED\n'.format(test))
            points = (test - 1) * 5
            results.append('Points: {:d}\n'.format(points))
            results.append('Total: {:.3f}, Stopped because of failure.'.format(total, failed))
            return results
    points = (test_count - failed) * 5
    results.append('Points: {:d}\n'.format(points))
    results.append('Total: {:.3f}, Failed: {:d}'.format(total, failed))
    return results


@celery.task(bind=True)
def run_task(self, path, problem, language, grade):
    if os.path.exists(os.path.join(basedir, path)):
        rmtree(os.path.join(basedir, path))
    unique_path = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
    os.makedirs(os.path.join(basedir, path))
    if language == 'c':
        sourcefile = unique_path + '.c'
        headerfile = unique_path + '.h'
        if os.path.isfile(headerfile):
            copy2(headerfile, os.path.join(basedir, path, '%s.h' % problem))
        copy2(sourcefile, os.path.join(basedir, path, '%s.c' % problem))
        try:
            subprocess.check_call(['gcc', '-Wall', '-O2', '-static', '%s.c' % problem, '-I.', '-o', '%s' % problem], stderr=subprocess.STDOUT, cwd=os.path.join(basedir, path))
        except subprocess.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    elif language == 'cpp':
        sourcefile = unique_path + '.cpp'
        headerfile = unique_path + '.h'
        if os.path.isfile(headerfile):
            copy2(headerfile, os.path.join(basedir, path, '%s.h' % problem))
        copy2(sourcefile, os.path.join(basedir, path, '%s.cpp' % problem))
        try:
            subprocess.check_output(['g++', '-std=c++11', '-Wall', '-O2', '-static', '%s.cpp' % problem, '-I.', '-o', '%s' % problem], stderr=subprocess.STDOUT, cwd=os.path.join(basedir, path))
        except subprocess.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    elif language == 'pas':
        sourcefile = unique_path + '.pas'
        copy2(sourcefile, os.path.join(basedir, path, '%s.pas' % problem))
        try:
            subprocess.check_call(['fpc', '-O2', '-Xs', '%s.pas' % problem, '-o%s' % problem], stderr=subprocess.STDOUT, cwd=os.path.join(basedir, path))
        except subprocess.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    elif language == 'java':
        sourcefile = unique_path + '.java'
        copy2(sourcefile, os.path.join(basedir, path, 'Main.java'))
        try:
            subprocess.check_call(['javac', 'Main.java'], stderr=subprocess.STDOUT, cwd=os.path.join(basedir, path))
        except subprocess.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    stdout = run_tests(path, problem, language, grade, number_of_tests(problem, grade))
    store_duration(path, stdout)
    rmtree(os.path.join(basedir, path))
    return {'status': stdout,
            'result': 'Task completed!'}


@app.route('/run/<path:path>', methods=['POST'])
def runtask(path):
    info = g.db.view("users/by_uploads", key=session.get('username'))
    for f in info:
        if path in f['id']:
            problem = f['value'][1]
            language = f['value'][2]
    run_task.apply_async(args=[path, problem, language, session.get('grade')], task_id=path)
    return jsonify({}), 202, {'Location': url_for('taskstatus', path=path)}


@app.route('/status/<path:path>')
def taskstatus(path):
    task = run_task.AsyncResult(path)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'running...'
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
