import logging
from datetime import timedelta
from azure.monitor.query import MetricsQueryClient
from azure.core.exceptions import HttpResponseError

class SqlMonitor:
    def __init__(self, credential, subscription_id, resource_group, instance_name):
        self.metrics_client = MetricsQueryClient(credential)
        self.resource_id = (
            f"/subscriptions/{subscription_id}/"
            f"resourceGroups/{resource_group}/"
            f"providers/Microsoft.Sql/managedInstances/{instance_name}"
        )
        self.instance_name = instance_name

    def check(self):
        """Checks SQL MI metrics and returns a list of alert messages."""
        logging.info(f"\nChecking SQL Managed Instance: {self.instance_name}")
        alerts = []
        try:
            metrics_data = self._query_metrics()
            if metrics_data:
                storage_alert = self._check_storage_usage(metrics_data)
                if storage_alert:
                    alerts.append(storage_alert)
        except Exception as e:
            error_message = f"Error checking SQL instance {self.instance_name}: {e}"
            logging.error(error_message)
            alerts.append(error_message)
        return alerts

    def _query_metrics(self):
        try:
            response = self.metrics_client.query_resource(
                resource_uri=self.resource_id,
                metric_names=["avg_cpu_percent", "storage_space_used_mb", "reserved_storage_mb"],
                timespan=timedelta(minutes=15), # Wider window for data availability
                granularity=timedelta(minutes=5),
                aggregations=["Average"]
            )
            return {metric.name: metric for metric in response.metrics}
        except HttpResponseError as e:
            logging.warning(f"  -> Failed to query metrics for {self.instance_name}: {e}")
            return None

    def _check_storage_usage(self, metrics_data):
        try:
            used_mb = self._get_latest_metric_value(metrics_data, "storage_space_used_mb")
            reserved_mb = self._get_latest_metric_value(metrics_data, "reserved_storage_mb")

            if used_mb is None or reserved_mb is None:
                return None # Not enough data

            if reserved_mb > 0:
                usage_percent = (used_mb / reserved_mb) * 100
                logging.debug(f"  -> Storage Usage: {usage_percent:.2f}% ({used_mb:.2f}MB / {reserved_mb:.2f}MB)")
                if usage_percent >= 90:
                    return f"SQL instance '{self.instance_name}' storage usage is at {usage_percent:.2f}%!"
            return None
        except (IndexError, TypeError) as e:
            logging.warning(f"  -> Could not process storage data for {self.instance_name}: {e}")
            return None

    def _get_latest_metric_value(self, metrics_data, metric_name):
        metric = metrics_data.get(metric_name)
        if metric and metric.timeseries and metric.timeseries[0].data:
            return metric.timeseries[0].data[-1].average # Get the most recent data point
        logging.warning(f"  -> Metric '{metric_name}' not available for {self.instance_name}.")
        return None
