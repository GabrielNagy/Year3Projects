  onChangeBuildsets: =>
    if not (@buildsets.$resolved and @buildsets.length > 0)
      return

    getChangeFromBbSourceStamp = (sourcestampdetails) ->
      fakeChange = {
        "revision": sourcestampdetails['revision'],
        "when_timestamp": sourcestampdetails['created_at'],
        "codebase": sourcestampdetails['codebase'],
        "repository": sourcestampdetails['repository'],
        "branch": sourcestampdetails['branch'],
      }
      if sourcestampdetails.hasOwnProperty('patch') and sourcestampdetails['patch']
        fakeChange["author"] = sourcestampdetails['patch']['author']
        fakeChange["comments"] = sourcestampdetails['patch']['comment']
      return fakeChange

    for buildset in @buildsets
      sourcestamps = buildset['sourcestamps']
      if sourcestamps.length != 1
        console.log("Unexpected sourcestamps for buildset " + buildset['bsid'])
      sourcestamp = sourcestamps[0]
      ssid = sourcestamp['ssid']
      if not @sourcestampsMap.hasOwnProperty(ssid)
        @sourcestampsMap[ssid] = {
          change: getChangeFromBbSourceStamp(sourcestamp),
          buildsets : []
        }
      @sourcestampsMap[ssid]['buildsets'].push(buildset['bsid'])
      @buildrequestsGetMap[buildset['bsid']] = @data.getBuildrequests(buildsetid: buildset['bsid'])
      @buildrequestsGetMap[buildset['bsid']].onChange = @onChangeBuildrequests

  onChangeBuildrequests: =>
    for id, buildreq of @buildrequestsGetMap
      if not buildreq.$resolved
        return

    for buildsetid, buildrequests of @buildrequestsGetMap
      @buildsetsMap[buildsetid] = {}
      @buildsetsMap[buildsetid]['pendingBuildrequests'] = {}
      @buildsetsMap[buildsetid]['claimedBuildrequests'] = {}

      for buildrequest in buildrequests
        buildrequestid = buildrequest['buildrequestid']

        if buildrequest["claimed"]
          @buildsGetMap[buildrequestid] = @data.getBuilds(buildrequestid: buildrequestid)
          @buildsGetMap[buildrequestid].onChange = @onChangeBuild
          @buildsetsMap[buildsetid]['claimedBuildrequests'][buildrequestid] = buildrequest
        else
          @buildsetsMap[buildsetid]['pendingBuildrequests'][buildrequestid] = buildrequest

  onChangeBuild: =>
    for id, bld of @buildsGetMap
      if not bld.$resolved
        return
    for buildrequestid, builds of @buildsGetMap
      @buildrequestsMap[buildrequestid] = {}
      for build in builds
        @buildrequestsMap[buildrequestid][build['buildid']] = build
    @generateBuildsMap()
