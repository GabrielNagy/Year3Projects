class BuildbotFriDashboard extends Controller
  constructor: ($scope, dataService, resultsService, @$uibModal) ->
    _.mixin($scope, resultsService)
    @data = dataService.open().closeOnDestroy($scope)

    $scope.sourcestampsMap = @sourcestampsMap = {}
    $scope.builds = @builds = {}
    $scope.buildrequests = @buildrequests = {}

    @buildrequestsMap = {}
    @buildsetsMap = {}

    @buildrequestsGetMap = {}
    @buildsGetMap = {}

    $scope.builders = @builders = @data.getBuilders()

    epochTime = Math.floor((new Date).getTime()/1000)
    earliestSubmittedTime = epochTime - (60 * 60 * 24 * 7)

    @buildsets = @data.getBuildsets(limit:128, order: "-bsid", submitted_at__gt:earliestSubmittedTime)
    @buildsets.onChange = @onChangeBuildsets

