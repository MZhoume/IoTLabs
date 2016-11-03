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
    DBManager.prototype.read = function (tableName, payload, callback) {
        var params = {
            TableName: tableName,
            Key: payload.key
        };
        this._db.get(params, callback);
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
        case 'read':
            db.read(tableName, payload, callback);
            break;
        case 'find':
            db.find(tableName, payload, callback);
            break;
        case 'location':
            var ip = payload.ip;
            request.get(GEO_CALL.format(ip), function (err, res, body) {
                if (res.statusCode === 200) {
                    var r = JSON.parse(body);
                    var lat_1 = r.lat;
                    var lon_1 = r.lon;
                    callback(null, "lat: " + lat_1 + " lon: " + lon_1);
                }
                else {
                    callback(new Error(err));
                }
            });
            break;
        case 'weather':
            var lon = payload.lon;
            var lat = payload.lat;
            request.get(WEATHER_CALL.format(lat, lon), function (err, res, body) {
                if (res.statusCode === 200) {
                    var r = JSON.parse(body);
                    var temp = r.main.temp - 273;
                    var weather = r.weather.main;
                    callback(null, "temp: " + temp + " weather: " + weather);
                }
                else {
                    callback(new Error(err));
                }
            });
            break;
        case 'tweet':
            var tweet_1 = payload.tweet;
            request.post(TWEET_CALL, { body: { api_key: "JMRG4J56B5YXNIPJ", status: tweet_1 }, json: true }, function (err, res, body) {
                if (res.statusCode === 200) {
                    callback(null, "TWEETED: " + tweet_1);
                }
                else {
                    callback(new Error(err));
                }
            });
            break;
    }
}
exports.handler = handler;
