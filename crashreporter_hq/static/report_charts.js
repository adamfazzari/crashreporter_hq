'use strict';


var app = angular.module('HQApp', []);

app.controller('ReportStats', function($scope, $http) {

});

app.directive('datechart', function($http) {
        return {
          restrict: 'A',
          link: function($scope, $elm, $attr) {
                // Create the data table.
                var data = new google.visualization.DataTable();
                var fail=function(err){ };
                var done = function(resp) {
                    var dates = [];
                    for (var ii=0; ii < resp.data.length; ii++){
                        // year, month (zero index), day, hour, Y-value
                        dates.push([new Date(resp.data[ii][0], resp.data[ii][1], resp.data[ii][2], resp.data[ii][3]), resp.data[ii][4]])
                    }
                    data.addColumn('date', 'Date of Report');
                    data.addColumn('number', 'Number of Reports');
                    data.addRows(dates);
                    // Set chart options
                    var options = {'title':'Crash Reports',
                                   'width':'100%',
                                   'height':600};
                    // Instantiate and draw our chart, passing in some options.
                    var chart = new google.visualization.LineChart($elm[0]);
                    chart.draw(data, options);
                };

                // Make a request to get the chart data
                $http.get('/reports/get_stats?type=date').then(done, fail);

          }
    }

});


app.directive('userchart', function($http) {
        return {
          restrict: 'A',
          link: function($scope, $elm, $attr) {
                // Create the data table.
                var data = new google.visualization.DataTable();
                var fail=function(err){ };
                var done = function(resp) {

                    data.addColumn('string', 'User');
                    data.addColumn('number', 'Number of Reports');
                    data.addRows(resp.data);
                    // Set chart options
                    var options = {'title':'Crash Reports',
                                   'width':'100%',
                                   'height':600};
                    // Instantiate and draw our chart, passing in some options.
                    var chart = new google.visualization.PieChart($elm[0]);
                    chart.draw(data, options);
                    };

                // Make a request to get the chart data
                $http.get('/reports/get_stats?type=user').then(done, fail);

                    }
            }
});

google.load('visualization', '1', {packages: ['corechart']});