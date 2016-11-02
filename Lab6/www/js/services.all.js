/// <reference path="../../../typings/index.d.ts" />
var addr = 'https://fit330b1q0.execute-api.us-east-1.amazonaws.com/lab6';
var HttpService = (function () {
    function HttpService(_http) {
        this._http = _http;
        this._urlBase = addr;
    }
    HttpService.prototype.init = function (urlBase) {
        if (urlBase.indexOf('/', urlBase.length - '/'.length) !== -1) {
            this._urlBase = urlBase.substr(0, urlBase.length - 1);
        }
        else {
            this._urlBase = urlBase;
        }
    };
    HttpService.prototype.get = function (url, callback) {
        this._http.get(this._urlBase + url)
            .success(function (d, n, h, c) { return callback.onSuccess(n, d); })
            .error(function (d, n, h, c) { return callback.onError(n, d); });
    };
    HttpService.prototype.post = function (url, payload, callback) {
        this._http.post(this._urlBase + url, payload)
            .success(function (d, n, h, c) { return callback.onSuccess(n, d); })
            .error(function (d, n, h, c) { return callback.onError(n, d); });
    };
    HttpService.$inject = ['$http'];
    return HttpService;
}());
angular.module('app')
    .service('HttpService', HttpService);
