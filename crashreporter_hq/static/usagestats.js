'use strict';


var app = angular.module('HQApp', []);

app.controller('UsageStats', function($scope, $http) {

});

app.directive('chart', function($http) {
        return {
          restrict: 'A',
          link: function($scope, $elm, $attr) {
                // Create the data table.
                var data = new google.visualization.DataTable();
                var fail=function(err){ };
                var done = function(resp) {
                    data.addColumn('string', 'User ID');
                    data.addColumn('number', 'Number of Reports');
                    data.addRows(resp.data);
                    // Set chart options
                    var options = {'title':'Breakdown of Crash Reports from Users',
                                   'width':800,
                                   'height':600};
                    // Instantiate and draw our chart, passing in some options.
                    var chart = new google.visualization.PieChart($elm[0]);
                    chart.draw(data, options);
                };

                // Make a request to get the chart data
                $http.get('/get_stats').then(done, fail);

          }
    }

});


google.load('visualization', '1', {packages: ['corechart']});