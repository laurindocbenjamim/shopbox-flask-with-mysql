import functools

from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Blueprint, flash, g, redirect, render_template, make_response, request, session, url_for,jsonify,
    abort
)
from flask_cors import CORS, cross_origin

from werkzeug.security import check_password_hash, generate_password_hash

from application.config.db_2 import init_db
from application.config.db import get_db
from mysql.connector import ProgrammingError
from application.config.jwtconfig import token_required, generate_token, decode_token, token_required
from functools import wraps

bp = Blueprint('apiauth', __name__, url_prefix='/api/auth')
CORS(bp)

@bp.route('/admin', methods=['GET','POST'])
@cross_origin(methods=['GET'])
#@token_required
def admin():
    try:
        response = decode_token(token=request.headers["Authorization"]) 
    except Exception as e:
        return f"Request finalized with the error: {e}"
    
    if len(response) > 0:
        if response['status_code'] == 200:

            conn = init_db() # Database connection
            try:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM peoples;")
                    obj = cursor.fetchall()
                    data = jsonify(obj)
                    return obj
            except AttributeError as e:
                return f" Database connection failed with the error: {e}"
            finally:
                conn.close()

    return jsonify({"message": "request failed", "status_code": response['status_code']}, response['status_code'])
# ============= USER REGISTRACTION FUNCTION ==================


@bp.route('/register', methods=('GET', 'POST'))
@cross_origin(methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.args.get('username')
        password = request.args.get('password')
        #username = request.form['username']
        #password = request.form['password']
        conn = init_db() 
        error = None

        if not username:
            error = 'Username is required.'
            abort(400)
        elif not password:
            error = 'Password is required.'
            abort(400)
        
        if error  is None:
           with conn.cursor() as cursor:
                sql = "INSERT INTO user (username, password) VALUES (%s, %s);"                
                try:
                    values = (username, generate_password_hash(password))
                    cursor.execute(sql,values,)
                    conn.commit()
                except Exception as err:
                    error = f"Error {err}."
                except ProgrammingError as err:
                    error = f"Programming error:  {err}"
                else:
                    return redirect(url_for("auth.login"))
            
        flash(error)
        
    return render_template('auth/register.html')


    # ======================= USER LOGGIN FUNCTION =====================
import json
@bp.route('/login', methods=['GET', 'POST'])
@cross_origin(methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.args.get('username')
        password = request.args.get('password')
        #username = request.form['username']
        #password = request.form['password']
      
        conn = init_db()
        error = None
        try:
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM `user` WHERE `username`=%s"
                cursor.execute(
                sql,
                (username,)
                )
                objt = cursor.fetchone()
                cursor.close()
                
                if  objt  is None:
                    error = 'Incorrect username.'
                elif not check_password_hash(objt['password'], password):
                    error = 'Incorrect password.'
                    return error

                if error is None:
                    session.clear()
                    session['user_id'] = objt['id']
                    token = generate_token(objt['username'])

                    return jsonify({"message": "User logged successfull", "object": objt, "token": token }, 200)
        except AttributeError as e:
            error = f" Database connection failed with the error: {e}"
        except ProgrammingError as e:
            error = f" Process failed with error: {e}"
        finally:
            conn.close()

        flash(error)

    return jsonify({"message": error, "object": []}, 500)


# MAKING AVAILABLE THE USER INFORMATIONS SINCE THEIR ID IS STORED IN THE SESSION

@bp.before_app_request
def load_logged_in_user():
    user_id = session. get('user_id')
    conn = init_db()
    
    try:
        if user_id is None:
            g.user = None
        else:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM `user` WHERE  `id` =%s", (user_id,))
                g.user = cursor.fetchone()
    except AttributeError as e:
        return jsonify({"message": e, "object":[]})  



# LOGOUT CLEANING ALL USER DATA FROM THE SESSION
        
@bp.route('/logout')
@cross_origin(supports_credentials=True,methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "User logged out", "object":[]}, 200)  



# REQUIRE A UTHENTICATION IN OTHER VIEWS 

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({"message": "No user identified", "object":[]}, 401)  
        
        return view(**kwargs)

    return wrapped_view
