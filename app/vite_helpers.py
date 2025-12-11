"""Flask helpers for Vite asset integration."""

import os
import json
from flask import current_app, url_for
from typing import Optional

# Configurable via environment variable for GitHub Codespaces
VITE_DEV_SERVER_URL = os.environ.get('VITE_DEV_SERVER_URL', 'http://localhost:5173')


def is_vite_dev_mode() -> bool:
  """Check if running in Vite development mode."""
  return current_app.config.get('VITE_DEV_MODE', os.environ.get('FLASK_ENV') == 'development')


def vite_asset(asset_path: str) -> str:
  """
  Resolve Vite asset path for production or development.

  Args:
    asset_path: Path to asset (e.g., 'main.ts')

  Returns:
    Full URL to asset
  """
  if is_vite_dev_mode():
    return f"{VITE_DEV_SERVER_URL}/{asset_path}"

  # Production: Read manifest.json
  static_folder = current_app.static_folder
  if not static_folder:
    return url_for('static', filename=f'dist/{asset_path}')

  manifest_path = os.path.join(static_folder, 'dist', '.vite', 'manifest.json')

  try:
    with open(manifest_path, 'r') as f:
      manifest = json.load(f)

    entry = manifest.get(asset_path)
    if entry:
      file_path = entry.get('file')
      if file_path:
        return url_for('static', filename=f'dist/{file_path}')
  except (FileNotFoundError, json.JSONDecodeError):
    pass

  # Fallback
  return url_for('static', filename=f'dist/{asset_path}')


def vite_hmr_client() -> Optional[str]:
  """Return Vite HMR client script tag in dev mode."""
  if is_vite_dev_mode():
    return f'<script type="module" src="{VITE_DEV_SERVER_URL}/@vite/client"></script>'
  return None
