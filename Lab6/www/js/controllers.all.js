/// <reference path="../../../typings/index.d.ts" />
/// <reference path="../services/HttpService.ts" />
var ViewCtrl = (function () {
    function ViewCtrl(_scope, _httpSvc) {
        this._scope = _scope;
        this._httpSvc = _httpSvc;
        _scope.accelChartConfig = {
            options: {},
            series: [{
                    data: _scope.data
                }],
            title: {
                text: 'Accel Data'
            },
            loading: false,
            size: {
                width: 640,
                height: 480
            },
            func: function (chart) {
                //setup some logic for the chart
            }
        };
        _httpSvc.get('/', {
            onSuccess: function (c, d) {
                _scope.hasError = false;
                _scope.error = '';
                _scope.data = d.Items;
            },
            onError: function (c, d) {
                _scope.data = [];
                _scope.hasError = true;
                _scope.error = 'Error: ' + c + " with message: " + d;
            }
        });
    }
    ViewCtrl.$inject = ['$scope', 'HttpService'];
    return ViewCtrl;
}());
angular.module('app')
    .controller('ViewCtrl', ViewCtrl);
