import os

from flask import (
    Flask, g, redirect, render_template, session, jsonify
)

from flask_cors import CORS

def create_app(test_config=None):
    # Create and configure the app
    application = Flask(__name__, instance_relative_config=True)
    
    CORS(application)

    application.config.from_mapping(
        SECRET_KEY="AB8D23A974B4C7B2ABB641668F9F9",
        DATABASE=os.path.join(application.instance_path, 'flaskr.mysql'),
    )

    if test_config is None:
        # Load  the  instance config if it exists, when not testing
        application.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        application.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(application.instance_path)
    except OSError:
        pass

    
    # import and call the database configuration
    #from . import db
    #from . config import db
    #db.init_app(app)

    # Import and call the blueprint
    from .modules import database_test
    application.register_blueprint(database_test.bp)
    #from . import auth
    from . modules.auth_module import auth
    from . modules.auth_module import authapi
    from . modules.auth_module import register
    application.register_blueprint(auth.bp)
    application.register_blueprint(authapi.bp)
    application.register_blueprint(register.bp)


    # Import the Blog Blueprint
    #from . modules.blog_module import blog
    #appication.register_blueprint(blog.bp)
    #appication.add_url_rule('/', endpoint='index')

    # Simple page that say hello
    @application.route("/test")
    def hello():
        return render_template('auth/login.html')
    
    return application