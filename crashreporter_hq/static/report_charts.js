'use strict';


var app = angular.module('HQApp', []);

app.controller('ReportStats', function($scope, $http) {

});


app.controller('hideAliased', function($scope, $http) {

});


app.directive('datechart', function($http) {
        return {
          restrict: 'A',
          link: function($scope, $elm, attr) {
                // Create the data table.

                var fail=function(err){ };
                var done = function(resp) {
                    // Instantiate and draw our chart
                    var data = new google.visualization.DataTable();
                    var chart = new google.visualization.LineChart($elm[0]);
                    // Set chart options
                    var options = {'title':'Report History',
                                   'width':'100%',
                                   'animation': {'startup': true,
                                                 'duration': 2000,
                                                 'easing': 'out'},
                                   'legend':'none',
                                   'height':'100%'};

                    var dates = [];
                    for (var ii=0; ii < resp.data.length; ii++){
                        // year, month (zero index), day, hour, Y-value
                        dates.push([new Date(resp.data[ii][0], resp.data[ii][1], resp.data[ii][2], resp.data[ii][3]), resp.data[ii][4]])
                    }
                    data.addColumn('date', 'Date of Report');
                    data.addColumn('number', 'Number of Reports');
                    data.addRows(dates);
                    chart.draw(data, options);
                };

                attr.$observe('aliased', function(value){
                    // Make a request to get the chart data
                    $http.get('/reports/get_stats?type=date&hide_aliased=' + value).then(done, fail);

                    });

                // Make a request to get the chart data
                // $http.get('/reports/get_stats?type=date').then(done, fail);

          }
    }

});


app.directive('userchart', function($http) {
        return {
          restrict: 'A',
          link: function($scope, $elm, attr) {
                // Create the data table.

                var fail=function(err){ };
                var done = function(resp) {
                    // Instantiate and draw our chart.
                    var data = new google.visualization.DataTable();
                    var chart = new google.visualization.PieChart($elm[0]);
                    // Set chart options
                    var options = {'title':'Report Breakdown',
                                   'width':'100%',
                                   'legend':'none',
                                   'is3D': true,
                                   'chartArea': {'width': '100%',
                                                 'height': '90%',
                                                 'easing': 'out'},
                                   'height':'100%'};

                    data.addColumn('string', 'User');
                    data.addColumn('number', 'Number of Reports');
                    data.addRows(resp.data);
                    chart.draw(data, options);
                    };

                attr.$observe('aliased', function(value){
                    // Make a request to get the chart data
                    $http.get('/reports/get_stats?type=user&hide_aliased=' + value).then(done, fail);

                    });

                // Make a request to get the chart data
                // $http.get('/reports/get_stats?type=user&show_aliased=False').then(done, fail);


              
                    }
            }
});

google.load('visualization', '1', {packages: ['corechart']});