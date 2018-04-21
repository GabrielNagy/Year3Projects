def is_python_file(change):
    for name in change.files:
        if name.endswith(".py"):
            return True
    return False
