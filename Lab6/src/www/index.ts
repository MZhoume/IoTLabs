/// <reference path="../../typings/index.d.ts" />

angular.module('app', ['ngRoute', 'nvd3'])
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