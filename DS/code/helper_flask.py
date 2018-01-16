from buildbot.util import datetime2epoch


def get_changed_files(patch_body):
    file_list = []
    files = patch_body.split("Index: ")

    for f in files:
        f2 = f.split("=")
        f2[0] = f2[0].strip(" :")
        file_list.append(f2[0])

    return file_list[1:]


def getChangeFromBbSourceStamp(sourcestampdetails):
    fakeChange = {
        "revision": str(sourcestampdetails['revision']),
        "when_timestamp": datetime2epoch(sourcestampdetails['created_at']),
        "codebase": str(sourcestampdetails['codebase']),
        "repository": str(sourcestampdetails['repository']),
        "branch": str(sourcestampdetails['branch']),
    }
    if sourcestampdetails['patch']:
        fakeChange["files"] = get_changed_files(sourcestampdetails['patch']['body'])
        fakeChange["author"] = str(sourcestampdetails['patch']['author'])
        fakeChange["comments"] = str(sourcestampdetails['patch']['comment'])
    return fakeChange
