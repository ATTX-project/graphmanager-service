import json
import falcon
import jsonschema
from functools import wraps


def validate(schema):
    """
    Validate against JSON schema an return something.

    Return a parsed object if there is a POST.
    If there is a get do not return anything just validate.
    """
    def decorator(func):
        """Decorator function."""
        @wraps(func)
        def wrapper(self, req, resp, *args, **kwargs):
            """Wrap it nicely."""
            if req.method == 'POST':
                try:
                    raw_json = req.stream.read()
                    obj = json.loads(raw_json.decode('utf-8'))
                except Exception:
                    raise falcon.HTTPBadRequest(
                        'Invalid data',
                        'Could not properly parse the provided data as JSON'
                    )
                try:
                    jsonschema.validate(obj, schema)
                except jsonschema.ValidationError as e:
                    raise falcon.HTTPBadRequest(
                        'Failed data validation',
                        e.message
                    )

                return func(self, req, resp, *args, parsed=obj, **kwargs)
            elif req.method == 'GET' or req.method == 'DELETE' and isinstance(req.path.split('/')[-1], int):
                return func(self, req, resp, *args, **kwargs)
        return wrapper
    return decorator


def valid_message(schema):
    """Validate messages against JSON schema an return something."""
    def decorator(func):
        """Decorator function."""
        @wraps(func)
        def wrapper(self, message, *args, **kwargs):
            """Wrap it nicely."""
            try:
                # raw_json = message.stream.read()
                # obj = json.loads(raw_json.decode('utf-8'))
                obj = json.loads(message.body)
            except Exception:
                raise ValueError(
                    'Invalid data',
                    'Could not properly parse the provided data as JSON'
                )
            try:
                jsonschema.validate(obj, schema)
            except jsonschema.ValidationError as e:
                raise falcon.HTTPBadRequest(
                    'Failed data validation',
                    e.message
                )
            return func(self, message, *args, **kwargs)
        return wrapper
    return decorator
