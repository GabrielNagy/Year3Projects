import flask_template

c['www']['plugins']['wsgi_dashboards'].append(
    {
        'name': 'fridashboard',  # what should appear in the URLs
        'caption': 'FRI Dashboard',  # what should be displayed in the UI
        'app': flask_template.fridashboardapp,
        'order': 5,  # priority in menu bar (lower order means higher priority)
        'icon': 'bars'  # icon to be shown in the UI (from fontawesome.io)
    }
)
