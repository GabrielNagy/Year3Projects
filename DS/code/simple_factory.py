from buildbot.plugins import util, steps

f = util.BuildFactory()
f.addSteps([
    steps.SVN(repourl="http://svn.example.org/trunk/"),
    steps.ShellCommand(command=["make", "all"]),
    steps.ShellCommand(command=["make", "test"])
])
