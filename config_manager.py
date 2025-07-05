
import sys
import os
import importlib.util

DEFAULT_CONFIG_CONTENT = """# --- General Azure Configuration ---
AZURE_SUBSCRIPTION_ID = "YOUR_SUBSCRIPTION_ID"

# --- Monitored Resources ---
SQL_MANAGED_INSTANCES = [
    {
        "resource_group": "YOUR_RESOURCE_GROUP",
        "instance_name": "YOUR_SQL_MANAGED_INSTANCE_NAME"
    },
]

# --- Email Alerting Configuration ---
SMTP_ENABLED = False
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
SMTP_USER = "your_email@example.com"
SMTP_PASSWORD = "your_email_password"
SMTP_FROM = "your_email@example.com"
SMTP_TO = ["recipient1@example.com"]
"""

def get_config_path():
    """Get the absolute path to the config.py file next to the executable or script."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), "config.py")
    else:
        return os.path.join(os.path.dirname(__file__), "config.py")

def _load_config_from_path(config_path):
    """Loads the config module from the specified path."""
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def _create_default_config(config_path):
    """Creates a default config.py file."""
    print(f"Config file not found. Creating a default one at: {config_path}")
    with open(config_path, "w") as f:
        f.write(DEFAULT_CONFIG_CONTENT)
    print("Default config.py created. Please edit it with your details and rerun the application.")

def initialize_config():
    """Checks for, creates, and loads the configuration file."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        _create_default_config(config_path)
        return None  # Return None to signal that the app should exit
    return _load_config_from_path(config_path)
