import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from werkzeug.security import check_password_hash, generate_password_hash

from app.config.db_2 import init_db
from app.config.db import get_db
from mysql.connector import ProgrammingError

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/view')
def index():
    return "Ola"

# ============= USER REGISTRACTION FUNCTION ==================

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.args.get('username')
        password = request.form['password']
        conn = init_db() 
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
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
        
    #return render_template('auth/register.html')
    return "Get it"


    # ======================= USER LOGGIN FUNCTION =====================

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        #username = request.form['username']
        #password = request.form['password']
        username = request.args.get('username')
        password = request.args.get('password')
        #db = get_db()
        conn = init_db()
        error = None
        try:
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM `user` WHERE `username`=%s"
                cursor.execute(
                sql,
                (username,)
                )
                user = cursor.fetchone()                
                
                if  user  is None:
                    error = 'Incorrect username.'
                elif not check_password_hash(user['password'], password):
                    error = 'Incorrect password.'
                    return error

                if error is None:
                    session.clear()
                    session['user_id'] = user['id']
                    return redirect(url_for('index'))
        except AttributeError as e:
            return f" Database connection failed with the error: {e}"
        except ProgrammingError as e:
            return f" Process failed with error: {e}"
        finally:
            conn.close()
       
        flash(error)

    return render_template('auth/login.html')


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
def logout():
    session.clear()
    return redirect(url_for('index'))



# REQUIRE A UTHENTICATION IN OTHER VIEWS 

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view
