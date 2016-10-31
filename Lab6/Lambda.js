/// <reference path="../typings/index.d.ts" />
"use strict";
var sdk = require('aws-sdk');
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
    switch (event.operation) {
        case 'create':
            var time = new Date().getTime();
            var payload = event.payload;
            payload['id'] = time;
            db.create(tableName, payload, callback);
            break;
        case 'read':
            db.read(tableName, event.payload, callback);
            break;
        case 'find':
            db.find(tableName, event.payload, callback);
            break;
    }
}
exports.handler = handler;
