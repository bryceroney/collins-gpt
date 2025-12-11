import os
from app import create_app

app = create_app()

if __name__ == "__main__":
  # Configure Vite dev mode based on Flask environment
  app.config['VITE_DEV_MODE'] = os.environ.get('FLASK_ENV') == 'development'
  app.run(debug=True, host='0.0.0.0', port=5000)
