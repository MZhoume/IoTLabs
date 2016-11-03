/// <reference path="../../../typings/index.d.ts" />
/// <reference path="../services/HttpService.ts" />

interface IAccelValue {
    x: number;
    y: number;
    z: number;
}

interface IChartData {
    values: [{ x: number, y: number }];
    key: string;
}

interface IViewScope extends angular.IScope {
    data: IChartData[];
    options: any;
    hasError: boolean;
    error: string;
}

function updateData(httpSvc: IHttpService, scope: IViewScope) {
    httpSvc.get('/', {
        onSuccess: (c, d) => {
            scope.hasError = false;
            scope.error = '';

            let sd = d.Items.sort((a, b) => a.id - b.id);
            scope.data = <IChartData[]>[{
                values: [],
                key: 'X'
            }, {
                values: [],
                key: 'Y'
            }, {
                values: [],
                key: 'Z'
            }];
            for (let i = 0; i < sd.length; i++) {
                scope.data[0].values.push({ x: i, y: sd[i].x });
                scope.data[1].values.push({ x: i, y: sd[i].y });
                scope.data[2].values.push({ x: i, y: sd[i].z });
            }
        },
        onError: (c, d) => {
            scope.hasError = true;
            scope.error = 'Error: ' + c + " with message: " + d;
        }
    });
    setTimeout(() => {
        updateData(httpSvc, scope);
    }, 1000);
}

class ViewCtrl {
    static $inject = ['$scope', 'HttpService'];
    constructor(
        private _scope: IViewScope,
        private _httpSvc: HttpService
    ) {
        _scope.options = {
            chart: {
                type: 'lineChart',
                height: 480,
                x: function(d) { return d.x; },
                y: function(d) { return d.y; },
                xAxis: {
                    axisLabel: 'Time Frame'
                },
                yAxis: {
                    axisLabel: 'Value'
                },
                useInteractiveGuideline: true,
            },
            title: {
                enable: true,
                text: 'Accel Data for Lab 6'
            }
        };

        updateData(_httpSvc, _scope);
    }
}

angular.module('app')
    .controller('ViewCtrl', ViewCtrl);
