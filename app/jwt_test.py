# -*- coding: utf-8 -*-
"""import depancies."""
import re
from flask import Flask, abort
from flask_restful import reqparse, Resource, Api, Resource, fields, marshal
from flasgger import Swagger
from flask_jwt import JWT, jwt_required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
api = Api(app, prefix="/api/v1")

USER_DATA = {
    "john.D@gmail.com": "qwerty1234"
}

USERS = [
    {
        'id':1,
        'name': u'John Doe',
        'email': u'john.D@gmail.com',
        'password': u'qwerty1234'
    },
    {
        'id':2,
        'name': u'Mary Jane',
        'email': u'jane.mary@yahoo.com',
        'password': u'qwerty1234'
    },
    {
        'id':3,
        'name': u'Antony Ng\'ang\'a',
        'email': u'tonny.nesh@gmail.com',
        'password': u'qwerty1234'
    }
]

class User(object):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "User(id='%s')" % self.id


def verify(email, password):
    if not (email and password):
        print(password)
        return False
    for user in USERS:
        if user['email'] == email:
            print(email)
            if user['password'] == password:
                print(password)
                return User(id=123)

def identity(payload):
    user_id = payload['identity']
    return {"user_id": user_id}

jwt = JWT(app, verify, identity)


class PrivateResource(Resource):
    @jwt_required()
    def get(self):
        return {"meaning_of_life": 42}


api.add_resource(PrivateResource, '/private')

if __name__ == '__main__':
    app.run(debug=True)
