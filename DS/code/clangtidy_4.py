def getResultSummary(self):
    cmdsummary = u""
    if self.errors and self.errors != "0":
        cmdsummary = "errors: " + self.errors
    if self.warnings and self.warnings != "0":
        if cmdsummary:
            cmdsummary = cmdsummary + ", "
            cmdsummary = cmdsummary + "warnings: " + self.warnings
    return {u'step': cmdsummary}
