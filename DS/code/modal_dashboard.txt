  selectBuild: (build) ->
    modal = @$uibModal.open
      templateUrl: "buildbot_fri_dashboard/views/modal.html"
      controller: 'dashboardModalController as modal'
      windowClass: 'modal-big'
      resolve:
        selectedBuild: -> build
