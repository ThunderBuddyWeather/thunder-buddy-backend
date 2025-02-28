import os
from datetime import datetime, timedelta
from flask import jsonify, request
import jwt  
from dotenv import load_dotenv
from functools import wraps

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

def get_remote_address(request):
    return request.remote_address

def encode_token(user_id):
    payload = {
        'exp': datetime.now() + timedelta(days=0, hours=1),
        'iat': datetime.now(),
        'sub': user_id
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
                print("Token:", token)
                payload = jwt.decode(token, SECRET_KEY, algorithms="HS256") 
            except jwt.ExpiredSignatureError: 
                return jsonify({'message': 'Token has expired', 'error': 'Unauthorized'}), 401
            except jwt.InvalidTokenError: 
                return jsonify({'message': 'Invalid Token', 'error': 'Unauthorized'}), 401
            if not token:
                return jsonify({'message': 'Authentication token is missing', 'error': 'Unauthorized'}), 401
        else:
            return jsonify({'message': 'Token is missing', 'error': 'Unauthorized'}), 401

    
        return f(*args, **kwargs)

    return decorated
