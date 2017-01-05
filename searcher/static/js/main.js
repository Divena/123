var module = angular.module("SearchApp", ['ngRoute', 'ngResource']);
module.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
})

module.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});


module.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
            when('/add_url', {
                templateUrl: static_url + 'html/addurl.html',
                controller: 'AddUrlCtrl'
            }).
            when('/search_page', {
                templateUrl: static_url + 'html/search.html',
                controller: 'SearchCtrl'
            });

    }]);


function SendPostData(url, data, scope, http)
{
    var config = {
 	       headers : {
   	        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
           }
        };
    http.post(url, data, config).success(function(answer){
        scope.answer = angular.fromJson(answer);
        if (url == 'search/')
        {
            scope.answer.sort(function(a, b){
                if (a.prior >= b.prior) return -1;
                if (a.prior < b.prior) return 1;
            });
            scope.status = 'What?';
        }
    });
}

module.controller('MainCtrl', function($scope, $http){

});

module.controller('SearchCtrl', function($scope, $http){
    $scope.status = 'What?';
    $scope.Submit = function(SearchForm)
    {
        if (SearchForm.$valid)
        {
            $scope.status = 'wait';
            var data = $.param({
                search : $scope.what_search
            });
            SendPostData('search/', data, $scope, $http);
        }
    }
});

module.controller('AddUrlCtrl', function($scope, $http){
    $scope.answer = {message : 'Enter urls you want to add in index'};
    $scope.Submit = function(AddUrlForm){
        $scope.answer.message = 'Please, wait';
        if (AddUrlForm.$valid)
        {
            var data = $.param({
                add_url : $scope.url_for_add
            });
            SendPostData('/add_url/', data, $scope, $http);
        }
    }
});
