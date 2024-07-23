from flask import Flask, render_template
from app.routes.todos import todos_bp
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    app.register_blueprint(todos_bp)

    @app.route('/')
    def home():
        return render_template('index.html')

    return app
