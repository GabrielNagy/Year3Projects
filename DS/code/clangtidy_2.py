def __init__(self, **kwargs):
    shell.ShellCommand.__init__(self, **kwargs)
    self.addLogObserver('stdio', logobserver.LineConsumerLogObserver(self.logConsumer))
    self.errors = "0"
    self.warnings = "0"
