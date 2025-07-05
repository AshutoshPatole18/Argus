
# --- General Azure Configuration ---
AZURE_SUBSCRIPTION_ID = "a4a861b9-271e-49d2-bfcc-384a971073e4"

# --- Monitored Resources ---
# List of SQL Managed Instances to monitor
# Each item is a dictionary with resource_group and instance_name
SQL_MANAGED_INSTANCES = [
    {
        "resource_group": "prod-japaneast-rg",
        "instance_name": "prod-japaneast-sql-mi-1"
    },
    {
        "resource_group": "non-prod-japaneast-rg",
        "instance_name": "non-prod-japaneast-sql-mi-sit-1"
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
SMTP_TO = ["recipient1@example.com", "recipient2@example.com"]


