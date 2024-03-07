import os

from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    CORS(app)

    app.config.from_mapping(
        SECRET_KEY="AB8D23A974B4C7B2ABB641668F9F9",
        DATABASE=os.path.join(app.instance_path, 'flaskr.mysql'),
    )

    if test_config is None:
        # Load  the  instance config if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    # import and call the database configuration
    #from . import db
    #from . config import db
    #db.init_app(app)

    # Import and call the blueprint
    from .modules import database_test
    app.register_blueprint(database_test.bp)
    #from . import auth
    from . modules.auth_module import auth
    from . modules.auth_module import authapi
    app.register_blueprint(auth.bp)
    app.register_blueprint(authapi.bp)

    # Import the Blog Blueprint
    #from . modules.blog_module import blog
    #app.register_blueprint(blog.bp)
    #app.add_url_rule('/', endpoint='index')

    # Simple page that say hello
    @app.route("/test")
    def hello():
        return "<h2>Hello, this a test </h2>"
    
    return app