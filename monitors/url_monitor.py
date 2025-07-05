
import requests

class UrlMonitor:
    """A generic monitor for checking website availability and content."""
    def __init__(self, monitor_name, url, check_string=None, timeout=10):
        self.monitor_name = monitor_name
        self.url = url
        self.check_string = check_string
        self.timeout = int(timeout)

    def check(self):
        """Performs the URL check and returns a list of alert messages."""
        print(f"\nChecking URL: {self.monitor_name} ({self.url})")
        alerts = []
        try:
            response = requests.get(self.url, timeout=self.timeout)

            if response.status_code >= 400:
                alert = f"URL '{self.monitor_name}' is down! Received status code {response.status_code}."
                print(f"  -> {alert}")
                alerts.append(alert)
            elif self.check_string and self.check_string not in response.text:
                alert = f"URL '{self.monitor_name}' is up, but the expected string was not found."
                print(f"  -> {alert}")
                alerts.append(alert)
            else:
                print(f"  -> Status: {response.status_code} OK")

        except requests.exceptions.RequestException as e:
            alert = f"Failed to connect to URL '{self.monitor_name}': {e}"
            print(f"  -> {alert}")
            alerts.append(alert)
        
        return alerts

