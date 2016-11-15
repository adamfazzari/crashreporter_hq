
var app = angular.module('hq-app', ['ngMaterial', 'ngMessages']);

// Change the templating symbol for angularjs so it doesn't conflict with Jinja
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

app.factory('reportService', function(){
   return {'reports': []}

});

app.controller('Hq', function($scope, $http) {

});


app.controller('HQController', function($scope, $http) {

});


app.controller('SearchResultsController', function($scope, $http, reportService){
    $scope.reportService = reportService;

    $scope.$watch('reportService.reports', function(newVal){
        $scope.reports = newVal;
    });

});

app.controller('SearchController', function($scope, $http, reportService){

    $scope.searchfields = [
                          {field: 'User', value: 'user_identifier'},
                          {field: 'Application Name', value: 'application_name'},
                          {field: 'Application Version', value: 'application_version'},
                          {field: 'After Version', value: 'after_version'},
                          {field: 'Before Version', value: 'before_version'},
                          {field: 'Report Number', value: 'id'},
                          {field: 'Error Message', value: 'error_message'},
                          {field: 'Error Type', value: 'error_type'},
                          {field: 'Date', value: 'date'},
                          {field: 'After Date', value: 'after_date'},
                          {field: 'Before Date', value: 'before_date'}
    ];


    $scope.searchform = {field1: '', value1: '',
                         field2: '', value2: '',
                         field3: '', value3: ''
                        };

    $scope.submitSearch = function() {
        $http.post('/search', JSON.stringify($scope.searchform)).success(function(data){
            reportService.reports = data.reports;
        })
    };

});

