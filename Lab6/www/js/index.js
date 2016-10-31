/// <reference path="../../typings/index.d.ts" />
angular.module('app', ['ngRoute', 'ngHighcharts'])
    .config(['$routeProvider', function ($route) {
        $route
            .when('/', {
            templateUrl: 'view/view.html',
            controller: 'ViewCtrl'
        })
            .otherwise({
            redirectTo: '/'
        });
    }]);
