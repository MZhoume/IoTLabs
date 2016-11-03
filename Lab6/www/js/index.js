/// <reference path="../../typings/index.d.ts" />
angular.module('app', ['ngRoute', 'nvd3'])
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
