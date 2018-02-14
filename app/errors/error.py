"""import depancies and methods."""

from flask import make_response, jsonify

def create_error_handler(app, errorno):
    @app.errorhandler(errorno)
    def handler(error):
        return
    return handler


def not_found_error(error):
    response_object = {
        'message': 'Object not found'
    }
    print('manenos')
    return make_response(jsonify(response_object)), 404

def method_error(error):
    response_object = {
        'message': 'Check the method'
    }
    return make_response(jsonify(response_object)), 405

def internal_error(error):
    response_object = {
        'message': 'Oops error from our side, weare working to solve it'
    }
    return make_response(jsonify(response_object)), 500     
