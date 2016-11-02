/// <reference path="../../../typings/index.d.ts" />
/// <reference path="../services/HttpService.ts" />

interface IAccelValue {
    x: number;
    y: number;
    z: number;
}

interface IViewScope extends angular.IScope {
    data: IAccelValue[];
    accelChartConfig: any;
    hasError: boolean;
    error: string;
}

class ViewCtrl {
    static $inject = ['$scope', 'HttpService'];
    constructor(
        private _scope: IViewScope,
        private _httpSvc: HttpService
    ) {
        _scope.accelChartConfig = {
            options: {
            },

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
            onSuccess: (c, d) => {
                _scope.hasError = false;
                _scope.error = '';

                _scope.data = d.Items;
            },
            onError: (c, d) => {
                _scope.data = [];
                _scope.hasError = true;
                _scope.error = 'Error: ' + c + " with message: " + d;
            }
        });
    }
}

angular.module('app')
    .controller('ViewCtrl', ViewCtrl);
