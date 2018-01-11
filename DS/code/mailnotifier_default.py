from buildbot.plugins import reporters
mn = reporters.MailNotifier(fromaddr="buildbot@example.org",
                            lookup="example.org")
c['services'].append(mn)
