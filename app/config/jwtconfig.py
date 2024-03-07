import jwt
import json
import requests

from datetime import datetime, timedelta, timezone
from flask import request, jsonify, current_app
from functools import wraps

"""
This method is used to cover the route in order to 
veriy is the user who are requiring the route acess have 
or not an acess token
"""
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        """
        This method is used to cover the route in order to 
        veriy is the user who are requiring the route acess have 
        or not an acess token
        """
        token = request.headers["Authorization"]
        token = str.replace(str(token), 'Bearer ', '')
        token = str(token).replace(" ", "")        
        #token = requests.get('token').json()
        if not token:
            return jsonify({'Alert!': 'Token is missing!', "token": token}, 401)        
        try:
            #payload = jwt.decode(token, current_app.config['SECRET_KEY'])
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], leeway=10, algorithms="HS256")
            return payload
        except jwt.ExpiredSignatureError as e:
            error = f"{e}"
            return jsonify({"error": error},401)
    return decorated

def decode_token(token):    
    token = str.replace(str(token), 'Bearer ', '')
    token = str(token).replace(" ", "")        
    #token = requests.get('token').json()
    if not token:
        return jsonify({'Alert!': 'Token is missing!', "token": token}, 401)        
    try:
        #payload = jwt.decode(token, current_app.config['SECRET_KEY'])
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], leeway=10, algorithms="HS256")
        payload["status_code"] = 200
        return payload
    except jwt.ExpiredSignatureError as e:
        error = f"{e}"
        return {"error": error, "status_code": 401}

"""  This method generate a token using the JWT library """
def generate_token(user):
    token = None
    try:
        date = datetime.utcnow() + timedelta(seconds=1800) # 1800 seconds is equal 30 minutes
        #date_serialized = json.dumps(date, default=str)   
        date_serialized = datetime.now(tz=timezone.utc) + timedelta(seconds=1800)

        token = jwt.encode({"user": user, 'exp': date_serialized, "nbf": datetime.now(tz=timezone.utc) },
                           current_app.config['SECRET_KEY'], algorithm="HS256")
       
    except Exception as e:
        token = f"{e}"
    
    return token



def filter_token_from_headers(headers):
    token = headers["Authorization"]
    token = str.replace(str(token), 'Bearer ', '')
    return token
    