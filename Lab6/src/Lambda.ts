/// <reference path="../typings/index.d.ts" />

import * as sdk from 'aws-sdk'
import * as lambda from 'aws-lambda'
import * as request from 'request'

if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
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

interface ICallback {
    (statusCode: number, body: any): void;
}

interface IDB {
    put(params, callback);
    scan(params, callback);
}

class DBManager {
    constructor(
        private _db: IDB
    ) { }

    create(tableName: string, item: {}, callback: lambda.Callback) {
        let params = {
            TableName: tableName,
            Item: item
        };

        this._db.put(params, callback);
    }

    find(tableName: string, payload, callback: lambda.Callback) {
        let params = {
            TableName: tableName,
            FilterExpression: payload.expression,
            ExpressionAttributeValues: payload.values
        };

        this._db.scan(params, callback);
    }
}

export function handler(event, context: lambda.Context, callback: lambda.Callback) {
    let dynamo = new sdk.DynamoDB.DocumentClient();
    let db = new DBManager(dynamo);
    let tableName = 'Accels';
    let payload = event.payload;

    switch (event.operation) {
        case 'create':
            let time = Math.floor(Date.now() / 1000);
            payload.id = time;
            db.create(tableName, payload, callback);
            break;

        case 'find':
            db.find(tableName, payload, callback);
            break;

        case 'get':
            request.get(ESP_CALL, (err, res, body) => {
                if (res.statusCode === 200) {
                    let r = body.split(',');
                    let x = parseFloat(r[0]);
                    let y = parseFloat(r[1]);
                    let z = parseFloat(r[2]);

                    let time = Math.floor(Date.now() / 1000);
                    let p = <any>{};
                    p.id = time;
                    p.x = x;
                    p.y = y;
                    p.z = z;
                    db.create(tableName, p, callback);
                } else {
                    callback(new Error(body));
                }
            });
            break;

        case 'location':
            let ip = payload.ip;
            request.get((<any>GEO_CALL).format(ip), (err, res, body) => {
                if (res.statusCode === 200) {
                    let r = JSON.parse(body);
                    let lat = r.lat;
                    let lon = r.lon;
                    request.get((<any>WEATHER_CALL).format(lat, lon), (err, res, body) => {
                        if (res.statusCode === 200) {
                            let r = JSON.parse(body);
                            let temp = Math.round((r.main.temp - 273) * 100) / 100;
                            let msg = r.weather[0].main;
                            let str = temp.toString() + 'C,' + msg;
                            request.get(ESP_CALL + 'w/' + str, (err, res, body) => {
                                if (res.statusCode === 200) {
                                    callback(null, JSON.stringify({ lat: lat, lon: lon, temp: temp, msg: msg }));
                                } else {
                                    callback(new Error(body));
                                }
                            });
                        } else {
                            callback(new Error(body));
                        }
                    });
                }
            });
            break;

        case 'weather':
            let lon = payload.lon;
            let lat = payload.lat;
            request.get((<any>WEATHER_CALL).format(lat, lon), (err, res, body) => {
                if (res.statusCode === 200) {
                    let r = JSON.parse(body);
                    let temp = Math.round((r.main.temp - 273) * 100) / 100;
                    let msg = r.weather[0].main;
                    let str = temp.toString() + 'C,' + msg;
                    request.get(ESP_CALL + 'w/' + str, (err, res, body) => {
                        if (res.statusCode === 200) {
                            callback(null, JSON.stringify({ temp: temp, msg: msg }));
                        } else {
                            callback(new Error(body));
                        }
                    });
                } else {
                    callback(new Error(body));
                }
            });
            break;

        case 'tweet':
            let tweet = payload.tweet;
            request.post(TWEET_CALL, { body: { api_key: "JMRG4J56B5YXNIPJ", status: tweet }, json: true }, (err, res, body) => {
                if (res.statusCode === 200) {
                    request.get(ESP_CALL + 't/' + tweet, (err, res, body) => {
                        if (res.statusCode === 200) {
                            callback(null, 'OK');
                        } else {
                            callback(new Error(body));
                        }
                    });
                } else {
                    callback(new Error(body));
                }
            })
            break;

        case 'command':
            let command = payload.command;
            request.get(ESP_CALL + command, (err, res, body) => {
                if (res.statusCode === 200) {
                    callback(null, 'OK');
                } else {
                    callback(new Error(body));
                }
            });
            break;
    }
}
