'use strict';


var app = angular.module('HQApp', []);

app.controller('UsageStats', function($scope, $http) {
    var done = function(resp) {
        $scope.states = resp.data['states'];
    }
    var fail=function(err){
        $scope.states = [];
    };
    $http.get('/usage/trackables').then(done, fail);
});

app.controller('stateSelection', function($scope, $http) {

});

app.controller('statisticSelection', function($scope, $http) {

});

app.controller('showaliasSelection', function($scope, $http) {

});

app.directive('statisticchart', function($http) {
        return {
                  restrict: 'A',
                  link: function($scope, $elm, attr) {
                        // Create the data table.
                        var fail=function(err){ };
                        console.log(attr);
                        var done = function(resp) {
                            var data = new google.visualization.DataTable();
                            data.addColumn('string', 'Statistic');
                            for (var i=0; i < resp.data['uuids'].length; i++) {
                                data.addColumn('number', resp.data['uuids'][i]);    
                            }
                            data.addRows(resp.data['counts']);
                            // Set chart options
                            var options = {'title':'Anonymous Statistics (Submissions from ' + resp.data['n_users'] + ' Users)',
                                           'isStacked':true,
                                           'width':'100%',
                                           'legend': 'none',
                                           'height':600};
                            // Instantiate and draw our chart, passing in some options.
                            var chart = new google.visualization.ColumnChart($elm[0]);
                            chart.draw(data, options);
                            };

                        // Make a request to get the chart data

                        var update = function(value){
                            // Make a request to get the chart data
                            var alias = (attr.showaliases=='') ? "0": attr.showaliases;
                            $http.get('/usage/plots/get_data?type=statistic&id=' + attr.plotid + '&hide_aliases=' + alias ).then(done, fail);
                            };

                        attr.$observe('plotid', update);
                        attr.$observe('showaliases', update);

                            }
            }
});

app.directive('statechart', function($http) {
        return {
          restrict: 'A',
          link: function(scope, elm, attr) {


                    var fail=function(err){
                        console.log(err)
                    };
                    var done = function(resp) {
                        // Create the data table.
                        var data = new google.visualization.DataTable();
                        data.addColumn('string', 'State');
                        data.addColumn('number', 'Count');
                        data.addRows(resp.data.counts);
                        // Set chart options
                        var options = {'title':resp.data.name,
                                       'width':'100%',
                                       'legend': 'none',
                                       'height':600};
                        // Instantiate and draw our chart, passing in some options.
                        var chart = new google.visualization.ColumnChart(elm[0]);
                        chart.draw(data, options);
                        };

                    var update = function(value){
                        // Make a request to get the chart data
                        $http.get('/usage/plots/get_data?type=state&name=' + attr.state + '&hide_aliases=' + attr.showaliases).then(done, fail);
                        };
              
                    attr.$observe('state', update);
                    attr.$observe('showaliases', update);

                    }
            }
});

google.load('visualization', '1', {packages: ['corechart']});