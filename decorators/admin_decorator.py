from flask import jsonify, make_response
from .token_utils import decode_token
from functools import wraps

def admin_required(func):
    """Decorator to check if the user is an admin."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        data, error_response = decode_token()
        if error_response:
            return error_response  # Return error if token decoding failed

        if data.get('admin'):
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'error': 'Admin access required'}), 401)

    return wrapper
