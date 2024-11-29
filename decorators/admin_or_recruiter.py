from flask import jsonify, make_response
from .token_utils import decode_token
from functools import wraps

def admin_or_recruiter_required(func):
    """Decorator to check if the user is an admin or a recruiter."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        data, error_response = decode_token()
        if error_response:
            return error_response  
        user_role = data.get('role')
        user_id = data.get('user_id')

        #Allow access if the user is an admin or a recruiter
        if data.get('admin', False) or user_role == 'Recruiter':
            #Inject `user_id` into kwargs if the function requires it
            if 'user_id' in func.__code__.co_varnames:
                kwargs['user_id'] = user_id
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'message': 'Admin or Recruiter access required'}), 403)

    return wrapper
