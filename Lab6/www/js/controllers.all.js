/// <reference path="../../../typings/index.d.ts" />
/// <reference path="../services/HttpService.ts" />
function updateData(httpSvc, scope) {
    httpSvc.get('/get', {
        onSuccess: function (c, d) { },
        onError: function (c, d) { }
    });
    httpSvc.get('/', {
        onSuccess: function (c, d) {
            scope.hasError = false;
            scope.error = '';
            var sd = d.Items.sort(function (a, b) { return a.id - b.id; });
            scope.data = [{
                    values: [],
                    key: 'X'
                }, {
                    values: [],
                    key: 'Y'
                }, {
                    values: [],
                    key: 'Z'
                }];
            for (var i = 0; i < sd.length; i++) {
                scope.data[0].values.push({ x: i, y: sd[i].x });
                scope.data[1].values.push({ x: i, y: sd[i].y });
                scope.data[2].values.push({ x: i, y: sd[i].z });
            }
        },
        onError: function (c, d) {
            scope.hasError = true;
            scope.error = 'Error: ' + c + " with message: " + d;
        }
    });
    setTimeout(function () {
        updateData(httpSvc, scope);
    }, 800);
}
var ViewCtrl = (function () {
    function ViewCtrl(_scope, _httpSvc) {
        this._scope = _scope;
        this._httpSvc = _httpSvc;
        _scope.options = {
            chart: {
                type: 'lineChart',
                height: 480,
                x: function (d) { return d.x; },
                y: function (d) { return d.y; },
                xAxis: {
                    axisLabel: 'Time Frame'
                },
                yAxis: {
                    axisLabel: 'Value'
                },
                useInteractiveGuideline: true
            },
            title: {
                enable: true,
                text: 'Accel Data for Lab 6'
            }
        };
        updateData(_httpSvc, _scope);
    }
    ViewCtrl.$inject = ['$scope', 'HttpService'];
    return ViewCtrl;
}());
angular.module('app')
    .controller('ViewCtrl', ViewCtrl);
