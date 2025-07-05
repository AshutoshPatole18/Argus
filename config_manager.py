
import os
import configparser

DEFAULT_CONFIG_CONTENT = """[General]
verbose = false

[Azure]
subscription_id = YOUR_SUBSCRIPTION_ID

[Email]
enabled = false
server = smtp.example.com
port = 587
use_tls = true
user = your_email@example.com
password = your_email_password
from_address = your_email@example.com
to_addresses = recipient1@example.com, recipient2@example.com

[Monitors.SQL.YourInstanceName] # Create a section for each instance
resource_group = YOUR_RESOURCE_GROUP

[Monitors.URL.GoogleExample]
url = https://www.google.com
# Optional: Look for specific text on the page
check_string = Google
timeout = 10 # Optional: defaults to 10 seconds

[Monitors.URL.AnotherSite]
url = https://www.github.com
check_string = GitHub

[Monitors.SSL.YourSSLDomain]
host = example.com # Just the domain, no https://
port = 443 # Optional: defaults to 443
"""

def get_config_dir():
    """Returns the OS-appropriate config directory path."""
    if os.name == 'nt': # Windows
        return os.path.join(os.environ['APPDATA'], 'ArgusSight')
    else: # Linux, macOS
        return os.path.join(os.path.expanduser('~'), '.config', 'ArgusSight')

def get_config_path():
    """Returns the full path to the config.ini file."""
    return os.path.join(get_config_dir(), 'config.ini')

def initialize_config():
    """Ensures the config directory and file exist, and returns the parsed config."""
    config_dir = get_config_dir()
    config_path = get_config_path()

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    if not os.path.exists(config_path):
        print(f"Config file not found. Creating a default one at: {config_path}")
        with open(config_path, "w") as f:
            f.write(DEFAULT_CONFIG_CONTENT)
        print("Default config.ini created. Please edit it with your details and rerun the application.")
        return None

    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def get_verbose_setting(config):
    """Returns the verbose setting from the config."""
    if config.has_option('General', 'verbose'):
        return config.getboolean('General', 'verbose')
    return False # Default to non-verbose if not specified
