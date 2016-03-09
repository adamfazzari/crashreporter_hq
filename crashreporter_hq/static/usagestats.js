'use strict';

angular.module('HQApp', ['googlechart'])


.controller('UsageStats', function($scope, $http) {
    var done=function(resp){
    var chart1 = {};
    chart1.type = "PieChart";
    chart1.data = resp.data;
    chart1.options = {
        displayExactValues: true,
        width: 600,
        height: 400,
        is3D: false,
        chartArea: {left:10,top:10,bottom:10,height:"100%"}
    };

    chart1.formatters = {
      number : [{
        columnNum: 1,
        pattern: "#,##0"
      }]
    };

    $scope.chart = chart1;
      };
    var fail=function(err){

      };

     $http.get('/get_stats')
     .then(done,fail);
});
