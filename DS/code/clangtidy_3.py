def evaluateCommand(self, cmd):
    res = shell.ShellCommand.evaluateCommand(self, cmd)
    if self.errors != "0":
        res = FAILURE
    if self.errors == "0" and self.warnings != "0":
        res = WARNINGS
    return res
