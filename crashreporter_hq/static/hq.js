
var app = angular.module('hq-app', ['ngMaterial', 'ngMessages']);

// Change the templating symbol for angularjs so it doesn't conflict with Jinja
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


app.controller('GroupController', function($scope, $http) {

    $scope.getReleases = function() {
        $http.get('/applications/releases').success(function (data) {
            $scope.application_releases = data;
        });
    };
    
    $scope.removeRelease = function(id) {
        $http.post('/applications/releases/remove?id=' + id).success(function() {
              $scope.getReleases();
        });
    };

    $scope.addRelease = function(name, version) {
        $http.post('/applications/releases/add?name=' + name + '&version='+ version).success(function() {
              $scope.getReleases();
        });
    };    
    
    
    $scope.getAliases = function() {
        $http.get('/aliases').success(function (data) {
            $scope.aliases = data;
        });
    };
    
    $scope.removeAlias = function(id) {
        $http.post('/aliases/remove?id=' + id).success(function() {
              $scope.getAliases();
        });
    };

    $scope.addAlias = function(uuid, alias) {
        $http.post('/aliases/add?uuid=' + uuid+ '&alias='+ alias).success(function() {
              $scope.getAliases();
        });
    };


    $scope.getPlots = function() {
        $http.get('/plots/statistics').success(function (data) {
            $scope.statistic_plots = data;
        });
    };

    $scope.addPlot = function(plotform) {
        stats = [].concat.apply([],plotform.statistics);
        data = {'name': plotform.name, 'statistics': stats};
        $http.post('/plots/statistics/add', data).success(function() {
            $scope.getPlots();
        });
    };

    $scope.removePlot = function(id) {
        $http.post('/plots/statistics/remove?id=' + id).success(function() {
              $scope.getPlots();
        });
    };
    
    $scope.addStatisticField = function() {
        $scope.PlotForm.statistics.push(['']);
    };

    $scope.getMembers = function() {
        $http.get('/groups/members').success(function (data) {
            $scope.group_members = data;
        });
    };
    
    $scope.manageMembers = function(user_id, action) {
        $http.post('/groups/members/'+ user_id + '?action='+ action).success(function() {
            $scope.getMembers();
        });
    };
    
    $scope.application_releases = [];
    $scope.aliases = [];
    $scope.statistic_plots = [];
    $scope.group_members = [];
    $scope.getReleases();
    $scope.getAliases();
    $scope.getPlots();
    $scope.getMembers();
    $scope.PlotForm = {'name': '', 'statistics': [['']], 'application': '', 'version': ''};
    $scope.AppReleaseForm = {'name': '', 'version': ''};
    $scope.currentNavItem = 'Plots';
    
});

app.controller('HQController', function($scope, $http, $mdSidenav) {

    $scope.toggleMenu = function (event) {
      $mdSidenav('leftNav').toggle()
    };

    $scope.onSwipeRight  = $scope.toggleMenu;


});

app.controller('SearchController', function($scope, $http){
    $scope.reports = [];
    $scope.n_affected_users = null;
    $scope.is_searching = false;
    $scope.reports_per_page_options = [{value:10},
                                       {value: 25},
                                       {value: 50},
                                       {value: 100}];
    $scope.alias_filter_options = [
                                  {field: 'No Filter', value: 'any'},
                                  {field: 'Only Aliases', value: 'only'},
                                  {field: 'No Aliases', value: 'none'},
                                  ];
    $scope.release_filter_options = [
                                  {field: 'No Filter', value: 'any'},
                                  {field: 'Releases Only', value: 'only'},
                                  {field: 'Development Only', value: 'none'},
                                  ];
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


    $scope.searchform = {filters: [['', '']],
                         page: 1, 
                         before_date: null,
                         after_date: null,
                         reports_per_page : 25,
                         related_to_id: null,
                         alias_filter: 'any',
                         release_filter: 'any',
                        };

    $scope.init = function(searchparams) {
        if (searchparams == undefined) {
            $scope.submitSearch();
        } else {
            for (key in searchparams) {
                $scope.searchform[key] = searchparams[key];
            }
            $scope.submitSearch();
        }
        console.log(searchparams);
    };

    $scope.addFilter = function() {
        $scope.searchform.filters.push(['', '']);
    };
    

    $scope.removeFilter = function(criteria) {
        $scope.searchform.filters.splice($scope.searchform.filters.indexOf(criteria), 1);
    };

    $scope.deleteReport = function(report_number) {
      $http.post('/reports/' + report_number + '/delete').success(function () {
          var r = null;
          for (var i=0; i < $scope.reports.length; i++) {
              r = $scope.reports[i];
              if (r.report_number == report_number) {
                  if (r.related_report_numbers.length == 1) {
                      $scope.reports.splice(i, 1);
                      break;
                  } else if (r.related_report_numbers.length > 1) {
                      // Remove the deleted report from the list of similar reports
                      r.related_report_numbers.splice(r.related_report_numbers.indexOf(r), 1);
                      // Set the visible report to another report in the list of similar reports
                      var next_related_report_id = r.related_report_numbers[r.related_report_numbers.length-1];
                      $http.get('/reports/' + next_related_report_id + '/info').success(function (report){
                          $scope.reports[i] = report;
                      });
                      break;
                  }
                  
              }
          }
          $scope.pagination.total_reports -=1;

      })
    };

    $scope.submitSearch = function(page) {
        $scope.is_searching = true;
        if (page == undefined) {
            $scope.searchform.page = 1;
        } else {
            $scope.searchform.page = page;
        }

        // Format the min and max date criteria into Day#/Month#/Year# string format
        var minDate = $scope.searchform.before_date;
        if (minDate != null && (minDate instanceof Date) ) {
            sdate = minDate.getDate().toString() + '/' + (minDate.getMonth() + 1).toString() + '/' + minDate.getFullYear().toString();
            $scope.searchform.before_date = sdate;
        }

        var maxDate = $scope.searchform.after_date;
        if (maxDate != null && (maxDate instanceof Date)) {
            sdate = maxDate.getDate().toString() + '/' + (maxDate.getMonth() + 1).toString() + '/' + maxDate.getFullYear().toString();
            $scope.searchform.after_date = sdate;
        }

        $http.post('/search', JSON.stringify($scope.searchform)).success(function(data){
            // Determine which pages to show in the pagination links
            pages = [];
            pagination_pages_to_show = 3;
            var leftpagestart = Math.max(data.page - pagination_pages_to_show, 1);
            var rightpageend= Math.min(leftpagestart+2*pagination_pages_to_show, data.max_page);
            for (var i=leftpagestart; i <= rightpageend; i++) {
                pages.push(i);
            }
            $scope.pagination = {page: data.page,
                                 pages: pages,
                                 max_page: data.max_page,
                                 total_reports: data.total_reports};
            $scope.reports = data.reports;
            $scope.n_affected_users = data.n_users_affected;
            $scope.is_searching = false;

        }).error(function() {
            $scope.is_searching = false;
        })
    };

    $scope.setRelatedGroup = function(related_to_id) {
        $scope.searchform.related_to_id = related_to_id;
        $scope.submitSearch();
    };

    $scope.removeRelatedGroup = function() {
        $scope.searchform.related_to_id = null;
        $scope.submitSearch();
    };

});


