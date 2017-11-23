from setuptools import setup

setup(
    name='upload_app',
    packages=['upload_app'],
    include_package_data=True,
    install_requires=[
        'celery',
        'flask',
        'flask_bcrypt',
        'flask_bootstrap',
        'flask_nav',
        'flask_recaptcha',
        'couchdbkit',
        'redis',
        'werkzeug',
        'wtforms'
    ],
)
