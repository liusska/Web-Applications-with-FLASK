from flask import request
from werkzeug.exceptions import BadRequest


def validate_schema(schema_name):
    def wrapper(func):
        def decorated_func(*args, **kwargs):
            data = request.get_json()
            schema = schema_name
            errors = schema.validate(data)
            if errors:
                raise BadRequest('...')
            return func(*args, **kwargs)
        return decorated_func
    return wrapper
