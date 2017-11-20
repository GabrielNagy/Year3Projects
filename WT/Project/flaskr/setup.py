from setuptools import setup

setup(
    name='flaskr',
    packages=['flaskr'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_bcrypt',
        'flask_bootstrap',
        'flask_nav',
        'flask_recaptcha',
        'couchdbkit',
        'werkzeug',
        'wtforms'
    ],
)
