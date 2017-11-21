from setuptools import setup

setup(
    name='upload-app',
    packages=['upload-app'],
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
