
import logging
import requests

class UrlMonitor:
    """A generic monitor for checking website availability and content."""
    def __init__(self, monitor_name, url, check_string=None, json_check=None, username=None, password=None, timeout=10):
        self.monitor_name = monitor_name
        self.url = url
        self.check_string = check_string
        self.json_check = json_check
        self.username = username
        self.password = password
        self.timeout = int(timeout)

    def check(self):
        """Performs the URL check and returns a list of alert messages."""
        logging.info(f"\nChecking URL: {self.monitor_name} ({self.url})")
        alerts = []
        try:
            auth = (self.username, self.password) if self.username and self.password else None
            response = requests.get(self.url, timeout=self.timeout, auth=auth)

            if response.status_code >= 400:
                alert = f"URL '{self.monitor_name}' is down! Received status code {response.status_code}."
                logging.warning(f"  -> {alert}")
                alerts.append(alert)
            elif self.check_string and self.check_string not in response.text:
                alert = f"URL '{self.monitor_name}' is up, but the expected string was not found."
                logging.warning(f"  -> {alert}")
                alerts.append(alert)
            elif self.json_check:
                try:
                    json_response = response.json()
                    for key, expected_value in self.json_check.items():
                        if key not in json_response or json_response[key] != expected_value:
                            alert = f"'{key}' does not match expected value. Expected: {expected_value}, Got: {json_response.get(key)}"
                            logging.warning(f"  -> {alert}")
                            alerts.append(alert)
                except ValueError:
                    alert = f"URL '{self.monitor_name}' is up, but response is not valid JSON."
                    logging.warning(f"  -> {alert}")
                    alerts.append(alert)
            else:
                logging.debug(f"  -> Status: {response.status_code} OK")

        except requests.exceptions.RequestException as e:
            alert = f"Failed to connect to URL '{self.monitor_name}': {e}"
            logging.error(f"  -> {alert}")
            alerts.append(alert)
        
        return alerts

