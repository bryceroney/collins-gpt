from flask import Flask
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
import os


def create_app():
  """Application factory pattern for creating Flask app.

  Loads environment variables from a local .env (development) and
  initializes CSRF protection for WTForms.
  """
  load_dotenv()
  app = Flask(__name__)

  # Configuration - prefer environment-provided SECRET_KEY in production
  app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

  # Initialize CSRF protection (Flask-WTF)
  csrf = CSRFProtect()
  csrf.init_app(app)

  # Register blueprints
  from app import routes
  app.register_blueprint(routes.bp)

  return app
