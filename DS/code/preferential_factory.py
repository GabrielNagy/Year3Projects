from buildbot.plugins import util, steps
from buildbot.process.results import FAILURE

f = util.BuildFactory()
f.addSteps([
    steps.SVN(repourl="http://svn.example.org/trunk/"),
    steps.ClangTidy(command=["clang-tidy", "src/*", "--", "-std=c++11"]),
    steps.Compile(command=["make", "test"], doStepIf=lambda step: step.build.executedSteps[-2].results != FAILURE),
    steps.ShellCommand(command=["rm", "-rf", "build/*"], alwaysRun=True)
])
