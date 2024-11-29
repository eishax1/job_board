from flask import jsonify, make_response
from decorators.token_utils import decode_token
from functools import wraps

def recruiter_required(func):
    """Decorator to check if the user is a recruiter or an admin."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        data, error_response = decode_token()
        if error_response:
            return error_response  #Return error if token decoding failed

        user_role = data.get('role')
        user_id = data.get('user_id')

        if user_role == 'Recruiter' or data.get('admin', False):
            #Inject `user_id` into kwargs if the function using the decorator requires it
            if 'user_id' in func.__code__.co_varnames:
                kwargs['user_id'] = user_id
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'message': 'Recruiter access required'}), 403)

    return wrapper
