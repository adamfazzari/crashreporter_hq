'use strict';


var app = angular.module('HQApp', []);

app.controller('UsageStats', function($scope, $http) {

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
                    for (var ii=0; ii < resp.data.date_data.length; ii++){
                        dates.push([new Date(resp.data.date_data[ii][0], resp.data.date_data[ii][1], resp.data.date_data[ii][2], resp.data.date_data[ii][3]), resp.data.date_data[ii][4]])
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
                $http.get('/get_stats').then(done, fail);

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
                    data.addRows(resp.data.user_data);
                    // Set chart options
                    var options = {'title':'Crash Reports',
                                   'width':'100%',
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


app.directive('columnchart', function($http) {
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
                $http.get('/get_stats2').then(done, fail);

                    }
            }
});


google.load('visualization', '1', {packages: ['corechart']});