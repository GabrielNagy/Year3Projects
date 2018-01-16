import os
import common
import time
from flask import Flask
from flask import render_template
from buildbot.data.resultspec import Filter
from buildbot.process.results import statusToString
from buildbot.util import datetime2epoch

fridashboardapp = Flask('test', root_path=os.path.dirname(__file__))
fridashboardapp.config['TEMPLATES_AUTO_RELOAD'] = True


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


@fridashboardapp.route("/index.html")
def main():
    bigData = {}
    epoch_time = int(time.time())
    earliestSubmittedTime = epoch_time - (60 * 60 * 24 * 7)  # last week
    out_file = open("/tmp/buildotTmpLogFriDash", "w")
    fribuilders = fridashboardapp.buildbot_api.dataGet("/builders", filters=[Filter("tags", "contains", ["fri"]), Filter("masterids", "ne", [[]])])
    buildsets = fridashboardapp.buildbot_api.dataGet("buildsets", limit=128, order=["-bsid"], filters=[Filter("submitted_at", "gt", [earliestSubmittedTime])])

    for buildset in buildsets:
        sourcestamps = buildset['sourcestamps']
        if len(sourcestamps[0]) != 1:
            out_file.write("ERROR: more that 1 sourcestamp for buildset" + str(buildset["bsid"]) + "\n")
        sourcestamp = sourcestamps[0]
        proj = sourcestamp['project']
        if proj != "fri":
            continue

        ssid = sourcestamp['ssid']
        if ssid not in bigData:
            bigData[ssid] = {}
            bigData[ssid]['change'] = common.getChangeFromBbSourceStamp(sourcestamp)
            bigData[ssid]['builders'] = {}

        buildrequests = fridashboardapp.buildbot_api.dataGet("buildrequests", filters=[Filter("buildsetid", "eq", [buildset['bsid']])])
        for buildrequest in buildrequests:
            id = buildrequest['builderid']
            if id not in bigData[ssid]['builders']:
                bigData[ssid]['builders'][id] = []

            if buildrequest["claimed"]:
                builds = fridashboardapp.buildbot_api.dataGet(("buildrequests", buildrequest["buildrequestid"], "builds"))
                for build in builds:
                    results_text = statusToString(build['results']).upper()
                    if results_text == 'NOT FINISHED':
                        results_text = 'PENDING pulse'

                    bigData[ssid]['builders'][id].append({
                        'type': 'build',
                        'number': build["number"],
                        'results_text': results_text
                    })
            else:
                bigData[ssid]['builders'][id].append({
                    'type': 'buildrequest',
                    'id': buildrequest["buildrequestid"],
                    'results_text': "UNKNOWN"
                })

    out_file.close()

    # fridashboard.html is a template inside the template directory
    return render_template('fridashboard.html', builders=fribuilders, bigdata=bigData)


@fridashboardapp.after_request
def response_minify(response):
    """
    minify html response to decrease site traffic
    """
    from htmlmin.main import minify
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            minify(response.get_data(as_text=True))
        )

        return response
    return response
