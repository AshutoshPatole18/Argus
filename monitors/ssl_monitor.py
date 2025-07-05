import ssl
import socket
from datetime import datetime

class SSLMonitor:
    def __init__(self, host, port=443):
        self.host = host
        self.port = port

    def check(self):
        context = ssl.create_default_context()
        try:
            with socket.create_connection((self.host, self.port)) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse the 'notAfter' field to get the expiration date
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    # Calculate days remaining
                    days_remaining = (not_after - datetime.now()).days
                    
                    alerts = []
                    if days_remaining < 15:
                        alerts.append(f"SSL certificate for {self.host} expires in {days_remaining} days!")
                    return alerts
        except Exception as e:
            return [f"Error checking SSL for {self.host}: {e}"]
