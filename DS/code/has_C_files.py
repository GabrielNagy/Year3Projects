def has_C_files(change):
    for name in change.files:
        if name.endswith(".c"):
            return True
    return False
