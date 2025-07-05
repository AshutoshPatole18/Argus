

import config_manager
import updater
from monitors.sql_monitor import SqlMonitor
import alerter
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

def main():
    """Main function to run all monitoring checks and send alerts."""
    updater.check_for_updates()

    config = config_manager.initialize_config()
    if not config:
        return # Exit if config was just created

    print("Starting ArgusSight tool...")

    try:
        credential = DefaultAzureCredential()
        print("Authentication successful.")
    except ClientAuthenticationError as e:
        print(f"Authentication failed: {e}")
        return

    all_alerts = []

    # Run SQL Monitors
    for section in config.sections():
        if section.startswith('Monitors.SQL.'):
            instance_name = section.split('.')[-1]
            instance_config = config[section]
            sql_monitor = SqlMonitor(
                credential=credential,
                subscription_id=config['Azure']['subscription_id'],
                resource_group=instance_config["resource_group"],
                instance_name=instance_name
            )
            alerts = sql_monitor.check()
            all_alerts.extend(alerts)

    # Send Alerts
    if all_alerts:
        subject = "Azure Monitoring Alert"
        body = "The following alerts were triggered:\n\n" + "\n".join(all_alerts)
        print(f"\n--- Preparing Alert ---\nSubject: {subject}\nBody:\n{body}")
        alerter.send_alert_email(subject, body, config)
    else:
        print("\nNo alerts triggered. All checks passed.")

if __name__ == "__main__":
    main()
