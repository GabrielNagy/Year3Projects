class ClangTidy(shell.ShellCommand):
    def logConsumer(self):
        while True:
            stream, line = yield
            self.gatherTestStatistics(line)

    def gatherTestStatistics(self, line):
        m = re.search('Errors:\s*(\d+)', line)
        if m:
            self.errors = m.group(1)
        m = re.search(r'Warnings:\s*(\d+)', line)
        if m:
            self.warnings = m.group(1)
