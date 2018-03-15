beforeEach ->
    module ($provide) ->
        $provide.service 'resultsService', -> results2class: ->
        null
    module ($provide) ->
        $provide.service '$uibModal', -> open: ->
        null
