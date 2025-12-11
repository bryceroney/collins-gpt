from flask import Flask


def create_app():
  """Application factory pattern for creating Flask app."""
  app = Flask(__name__)

  # Configuration
  app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

  # Register blueprints
  from app import routes
  app.register_blueprint(routes.bp)

  return app
