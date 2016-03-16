'use strict';


var app = angular.module('HQApp', []);

app.controller('UsageStats', function($scope, $http) {

});

app.directive('statisticchart', function($http) {
        return {
          restrict: 'A',
          link: function($scope, $elm, $attr) {
                // Create the data table.
                var data = new google.visualization.DataTable();
                var fail=function(err){ };
                var done = function(resp) {

                    data.addColumn('string', 'Statistic');
                    data.addColumn('number', 'Count');
                    data.addRows(resp.data.statistic);
                    data.addRows(resp.data.state);
                    // Set chart options
                    var options = {'title':'Anonymous Statistics',
                                   'width':'100%',
                                   'height':600};
                    // Instantiate and draw our chart, passing in some options.
                    var chart = new google.visualization.ColumnChart($elm[0]);
                    chart.draw(data, options);
                    };

                // Make a request to get the chart data
                $http.get('/usage/get_stats').then(done, fail);

                    }
            }
});


google.load('visualization', '1', {packages: ['corechart']});