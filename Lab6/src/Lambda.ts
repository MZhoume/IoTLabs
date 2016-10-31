/// <reference path="../typings/index.d.ts" />

import * as sdk from 'aws-sdk'
import * as lambda from 'aws-lambda'
import * as request from 'request'

interface IDB {
    put(params, callback);
    get(params, callback);
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

    read(tableName: string, payload, callback: lambda.Callback) {
        let params = {
            TableName: tableName,
            Key: payload.key
        };

        this._db.get(params, callback);
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

    switch (event.operation) {
        case 'create':
            let time = new Date().getTime();
            let payload = event.payload;
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
