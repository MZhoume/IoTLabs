/// <reference path="../../typings/index.d.ts" />

angular.module('app', ['ngRoute', 'ngHighcharts'])
.config(['$routeProvider', ($route: angular.route.IRouteProvider) => {
    $route
    .when('/', {
        templateUrl: 'view/view.html',
        controller: 'ViewCtrl'
    })
    .otherwise({
        redirectTo: '/'
    });
}]);