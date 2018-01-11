from buildbot.plugins import reporters
from mailnotifier import IcdCslToEmail

mailMap = {
    'cross_ci': 'cross_ci@alcatel-lucent.com',
}

template=u'''\
<h4>Build status: {{ summary }}</h4>
<p> Worker used: {{ workername }}</p>
{% for step in build['steps'] %}
<p> {{ step['name'] }}: {{step['state_string']}}</p>
{% endfor %}
<p><b> -- The Buildbot</b></p>
'''

m = reporters.MailNotifier(
    fromaddr="cross_ci@nokia.com",  # the address from which mail is sent
    tags=["cas"],  # only send for builders that have this tag; useful for multi-project masters
    lookup=mailnotifier.IcdCslToEmail(mailMap),  # our lookup function that takes the mailMap dict as an argument
    buildSetSummary=True,  # show a summary of the whole buildset in the e-mail
    messageFormatter=reporters.MessageFormatter(
        template=template, template_type='html',
        wantProperties=True, wantSteps=True))  # the HTML template to use in the message body

c['services'].append(m)
