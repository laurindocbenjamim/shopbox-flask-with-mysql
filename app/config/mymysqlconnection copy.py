import logging
import time
import mysql.connector

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
            return mysql.connector(**config)
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
            time.sleep(**attempt)
            attempt +=1
    return None






