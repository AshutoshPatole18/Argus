import config_manager
import updater
from monitors.sql_monitor import SqlMonitor
from monitors.url_monitor import UrlMonitor
from monitors.ssl_monitor import SSLMonitor
import alerter
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
import threading
import queue
import logging

def run_monitor_in_thread(monitor_instance, alerts_queue):
    """Wrapper function to run a monitor's check method in a thread and put results into a queue."""
    try:
        alerts = monitor_instance.check()
        if alerts:
            alerts_queue.put(alerts)
    except Exception as e:
        alerts_queue.put([f"Error running monitor {monitor_instance.__class__.__name__}: {e}"])

def main():
    """Main function to run all monitoring checks and send alerts."""
    updater.check_for_updates()

    config = config_manager.initialize_config()
    if not config:
        return # Exit if config was just created

    # Configure logging based on verbose setting
    verbose = config_manager.get_verbose_setting(config)
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

    # Suppress azure.identity logs
    logging.getLogger("azure.identity").setLevel(logging.ERROR)

    logging.info("Starting ArgusSight tool...")

    try:
        credential = DefaultAzureCredential()
        logging.debug("Authentication successful.")
    except ClientAuthenticationError as e:
        logging.warning(f"Authentication failed: {e}")
        # For URL checks, we don't need to exit if Azure auth fails
        credential = None 

    threads = []
    alerts_queue = queue.Queue()

    # Dynamically run all monitors defined in config in separate threads
    for section in config.sections():
        if section.startswith('Monitors.SQL.'):
            if not credential:
                logging.warning("Skipping SQL monitors due to authentication failure.")
                continue
            instance_name = section.split('.')[-1]
            instance_config = config[section]
            sql_monitor = SqlMonitor(
                credential=credential,
                subscription_id=config['Azure']['subscription_id'],
                resource_group=instance_config["resource_group"],
                instance_name=instance_name
            )
            thread = threading.Thread(target=run_monitor_in_thread, args=(sql_monitor, alerts_queue))
            threads.append(thread)
            thread.start()
        
        elif section.startswith('Monitors.URL.'):
            monitor_name = section.split('.')[-1]
            url_config = config[section]
            url_monitor = UrlMonitor(
                monitor_name=monitor_name,
                url=url_config['url'],
                check_string=url_config.get('check_string'),
                timeout=url_config.getint('timeout', 10) # Use getint for integer conversion
            )
            thread = threading.Thread(target=run_monitor_in_thread, args=(url_monitor, alerts_queue))
            threads.append(thread)
            thread.start()
        
        elif section.startswith('Monitors.SSL.'):
            monitor_name = section.split('.')[-1]
            ssl_config = config[section]
            ssl_monitor = SSLMonitor(
                host=ssl_config['host'],
                port=ssl_config.getint('port', 443)
            )
            thread = threading.Thread(target=run_monitor_in_thread, args=(ssl_monitor, alerts_queue))
            threads.append(thread)
            thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect all alerts from the queue
    all_alerts = []
    while not alerts_queue.empty():
        all_alerts.extend(alerts_queue.get())

    # Send Alerts
    if all_alerts:
        subject = "ArgusSight Monitoring Alert"
        body = "The following alerts were triggered:\n\n" + "\n".join(all_alerts)
        if verbose:
            logging.info(f"\n--- Preparing Alert ---\nSubject: {subject}\nBody:\n{body}")
        alerter.send_alert_email(subject, body, config)
    else:
        logging.info("\nNo alerts triggered. All checks passed.")

if __name__ == "__main__":
    main()
