import click
import logging
import time

import mysql.connector
from mysql.connector import errorcode

""" SET UP A LOGGER """
def create_logger_file():
   
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Log to console
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    #Log to a file
    file_handler = logging.FileHandler("mysql-conn-error.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


"""   Create a connection with mysql """
def connect_to_mysql(config, attempts=3, delay=2):
    logger = create_logger_file()
    attempt = 1
    #Implement a recoonection routine
    while attempt < attempts + 1:
        try:
            return mysql.connector.connect(**config)
        except (mysql.connector.Error, IOError) as err:
            if(attempts is attempt):
                #Attempts to reconnect failed; Returning none
                logger.info("Failed to connect, existing without a connection: %s", err)
                return None
            logger.info(
                "Connection failed: %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts - 1
            )
            # Progressive reconnect delay
            #time.sleep(**attempt)
            
            time.sleep(attempt)
            attempt +=1
    return None



#from flask import current_app, g 

def get_db():
    try:
        config = {
            'user': 'root',
            'password': '',
            'host': '127.0.0.1',
            'database': 'flask',
            'raise_on_warnings': True,
            'charset': 'utf8mb4'
        }

        #cnx = mysql.connector.connect(**config)
        cnx = connect_to_mysql(config, attempts=3)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(f"Process finalized with error: {err}")
    else:
        cnx.close()
    finally:
        print("Process finalized...")
  

def close_db(e=None):
    db = init_db()
    #cursor = mysql.cursor()
    db.close()
    return f"None"

def init_db():
    try:
        db = get_db()
        return db
        #with current_app.open_resource('schema.sql') as f:
            #cursor.execute(f.read().decode('utf8'))
    except RecursionError as e:
        return f"Error to start database {e}"


