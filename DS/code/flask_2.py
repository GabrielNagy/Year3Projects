    for buildset in buildsets:
        sourcestamps = buildset['sourcestamps']
        if len(sourcestamps[0]) != 1:
            out_file.write("ERROR: more that 1 sourcestamp for buildset" + str(buildset["bsid"]) + "\n")
        sourcestamp = sourcestamps[0]
        proj = sourcestamp['project']
        if proj != "fri":  # only go on if we have the desired project
            continue

        ssid = sourcestamp['ssid']
        if ssid not in bigData:
            bigData[ssid] = {}
            bigData[ssid]['change'] = getChangeFromBbSourceStamp(sourcestamp)
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
