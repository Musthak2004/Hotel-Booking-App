import os
import sys
from pathlib import Path

# ---- USER MUST UPDATE THIS ----
YOUR_PYTHONANYWHERE_USERNAME = "yourusername"
PROJECT_DIR = f"/home/{YOUR_PYTHONANYWHERE_USERNAME}/hotel_booking"
VENV_DIR = f"/home/{YOUR_PYTHONANYWHERE_USERNAME}/.virtualenvs/hotel_booking"
# --------------------------------

path = PROJECT_DIR
if path not in sys.path:
    sys.path.append(path)

activate_this = os.path.join(VENV_DIR, "bin", "activate_this.py")
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {"__file__": activate_this})

os.environ["DJANGO_SETTINGS_MODULE"] = "django_project.settings"

# Load .env file if it exists
env_path = Path(PROJECT_DIR) / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
