/// <reference path="../typings/index.d.ts" />
"use strict";
var sdk = require('aws-sdk');
var request = require('request');
if (!String.prototype.format) {
    String.prototype.format = function () {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match;
        });
    };
}
var GEO_CALL = 'http://ip-api.com/json/{0}';
var WEATHER_CALL = 'http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid=9bf0414bd85039152b7c1df96199a832';
var TWEET_CALL = 'https://api.thingspeak.com/apps/thingtweet/1/statuses/update';
var ESP_CALL = '/';
var DBManager = (function () {
    function DBManager(_db) {
        this._db = _db;
    }
    DBManager.prototype.create = function (tableName, item, callback) {
        var params = {
            TableName: tableName,
            Item: item
        };
        this._db.put(params, callback);
    };
    DBManager.prototype.find = function (tableName, payload, callback) {
        var params = {
            TableName: tableName,
            FilterExpression: payload.expression,
            ExpressionAttributeValues: payload.values
        };
        this._db.scan(params, callback);
    };
    return DBManager;
}());
function handler(event, context, callback) {
    var dynamo = new sdk.DynamoDB.DocumentClient();
    var db = new DBManager(dynamo);
    var tableName = 'Accels';
    var payload = event.payload;
    switch (event.operation) {
        case 'create':
            var time = Math.floor(Date.now() / 1000);
            payload.id = time;
            db.create(tableName, payload, callback);
            break;
        case 'find':
            db.find(tableName, payload, callback);
            break;
        case 'get':
            request.get(ESP_CALL, function (err, res, body) {
                if (res.statusCode === 200) {
                    var r = body.split(',');
                    var x = parseFloat(r[0]);
                    var y = parseFloat(r[1]);
                    var z = parseFloat(r[2]);
                    var time_1 = Math.floor(Date.now() / 1000);
                    var p = {};
                    p.id = time_1;
                    p.x = x;
                    p.y = y;
                    p.z = z;
                    db.create(tableName, p, callback);
                }
                else {
                    callback(new Error(body));
                }
            });
            break;
        case 'location':
            var ip = payload.ip;
            request.get(GEO_CALL.format(ip), function (err, res, body) {
                if (res.statusCode === 200) {
                    var r = JSON.parse(body);
                    var lat_1 = r.lat;
                    var lon_1 = r.lon;
                    request.get(WEATHER_CALL.format(lat_1, lon_1), function (err, res, body) {
                        if (res.statusCode === 200) {
                            var r_1 = JSON.parse(body);
                            var temp_1 = Math.round((r_1.main.temp - 273) * 100) / 100;
                            var msg_1 = r_1.weather[0].main;
                            var str = temp_1.toString() + 'C,' + msg_1;
                            request.get(ESP_CALL + 'w/' + str, function (err, res, body) {
                                if (res.statusCode === 200) {
                                    callback(null, JSON.stringify({ lat: lat_1, lon: lon_1, temp: temp_1, msg: msg_1 }));
                                }
                                else {
                                    callback(new Error(body));
                                }
                            });
                        }
                        else {
                            callback(new Error(body));
                        }
                    });
                }
            });
            break;
        case 'weather':
            var lon = payload.lon;
            var lat = payload.lat;
            request.get(WEATHER_CALL.format(lat, lon), function (err, res, body) {
                if (res.statusCode === 200) {
                    var r = JSON.parse(body);
                    var temp_2 = Math.round((r.main.temp - 273) * 100) / 100;
                    var msg_2 = r.weather[0].main;
                    var str = temp_2.toString() + 'C,' + msg_2;
                    request.get(ESP_CALL + 'w/' + str, function (err, res, body) {
                        if (res.statusCode === 200) {
                            callback(null, JSON.stringify({ temp: temp_2, msg: msg_2 }));
                        }
                        else {
                            callback(new Error(body));
                        }
                    });
                }
                else {
                    callback(new Error(body));
                }
            });
            break;
        case 'tweet':
            var tweet_1 = payload.tweet;
            request.post(TWEET_CALL, { body: { api_key: "JMRG4J56B5YXNIPJ", status: tweet_1 }, json: true }, function (err, res, body) {
                if (res.statusCode === 200) {
                    request.get(ESP_CALL + 't/' + tweet_1, function (err, res, body) {
                        if (res.statusCode === 200) {
                            callback(null, 'OK');
                        }
                        else {
                            callback(new Error(body));
                        }
                    });
                }
                else {
                    callback(new Error(body));
                }
            });
            break;
        case 'command':
            var command = payload.command;
            request.get(ESP_CALL + command, function (err, res, body) {
                if (res.statusCode === 200) {
                    callback(null, 'OK');
                }
                else {
                    callback(new Error(body));
                }
            });
            break;
    }
}
exports.handler = handler;
