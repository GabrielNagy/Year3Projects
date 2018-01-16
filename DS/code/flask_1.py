import os
import time
from flask import Flask
from buildbot.data.resultspec import Filter

fridashboardapp = Flask('test', root_path=os.path.dirname(__file__))
fridashboardapp.config['TEMPLATES_AUTO_RELOAD'] = True


@fridashboardapp.route("/index.html")
def main():
    bigData = {}
    epoch_time = int(time.time())
    earliestSubmittedTime = epoch_time - (60 * 60 * 24 * 7)  # last week
    out_file = open("/tmp/buildotTmpLogFriDash", "w")
    fribuilders = fridashboardapp.buildbot_api.dataGet("/builders", filters=[Filter("tags", "contains", ["fri"]), Filter("masterids", "ne", [[]])])
    buildsets = fridashboardapp.buildbot_api.dataGet("buildsets", limit=128, order=["-bsid"], filters=[Filter("submitted_at", "gt", [earliestSubmittedTime])])
