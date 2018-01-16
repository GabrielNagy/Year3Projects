import flask_template

c['www']['plugins']['wsgi_dashboards'].append(
    {
        'name': 'fridashboard',  # as used in URLs
        'caption': 'FRI Dashboard',  # Title displayed in the UI'
        'app': flask_template.fridashboardapp,
        # priority of the dashboard in the left menu (lower is higher in the
        # menu)
        'order': 5,
        # available icon list can be found at http://fontawesome.io/icons/
        'icon': 'bars'
    }
)
