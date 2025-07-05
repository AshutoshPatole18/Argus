

import logging
from datetime import timedelta
from azure.monitor.query import MetricsQueryClient
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError

class VmMonitor:
    def __init__(self, credential, subscription_id, resource_group, vm_name, config):
        self.metrics_client = MetricsQueryClient(credential)
        self.compute_client = ComputeManagementClient(credential, subscription_id)
        self.resource_group = resource_group
        self.vm_name = vm_name
        self.resource_id = (
            f"/subscriptions/{subscription_id}/"
            f"resourceGroups/{resource_group}/"
            f"providers/Microsoft.Compute/virtualMachines/{vm_name}"
        )
        self.config = config

    def check(self):
        """Checks VM status and metrics, returns a list of alert messages."""
        logging.info(f"\nChecking Virtual Machine: {self.vm_name}")
        alerts = []
        try:
            # Check VM Status first
            status_alert = self._check_vm_status()
            if status_alert:
                alerts.append(status_alert)
                # If VM is not running, don't check metrics
                return alerts

            # Check Metrics
            metrics_data = self._query_metrics()
            if metrics_data:
                cpu_alert = self._check_cpu_usage(metrics_data)
                if cpu_alert:
                    alerts.append(cpu_alert)
                
                mem_alert = self._check_memory_usage(metrics_data)
                if mem_alert:
                    alerts.append(mem_alert)

        except Exception as e:
            error_message = f"Error checking VM {self.vm_name}: {e}"
            logging.error(error_message)
            alerts.append(error_message)
        return alerts

    def _check_vm_status(self):
        """Checks the power state of the VM."""
        try:
            instance_view = self.compute_client.virtual_machines.instance_view(
                self.resource_group, self.vm_name
            )
            status = next((s for s in instance_view.statuses if s.code.startswith('PowerState/')), None)
            if status:
                vm_state = status.display_status
                logging.debug(f"  -> VM State: {vm_state}")
                if vm_state != "VM running":
                    return f"VM '{self.vm_name}' is not in a running state. Current state: {vm_state}."
            return None
        except HttpResponseError as e:
            logging.warning(f"  -> Failed to get VM status for {self.vm_name}: {e}")
            # Return the error as an alert because this is a critical check
            return f"Could not retrieve status for VM '{self.vm_name}'. It may be deallocated or deleted."


    def _query_metrics(self):
        """Queries all required VM metrics in a single call."""
        try:
            response = self.metrics_client.query_resource(
                resource_uri=self.resource_id,
                metric_names=["Percentage CPU", "Available Memory Bytes"],
                timespan=timedelta(minutes=15),
                granularity=timedelta(minutes=5),
                aggregations=["Average"]
            )
            return {metric.name: metric for metric in response.metrics}
        except HttpResponseError as e:
            logging.warning(f"  -> Failed to query metrics for {self.vm_name}: {e}")
            return None

    def _get_latest_metric_value(self, metrics_data, metric_name):
        metric = metrics_data.get(metric_name)
        if metric and metric.timeseries and metric.timeseries[0].data:
            return metric.timeseries[0].data[-1].average
        logging.warning(f"  -> Metric '{metric_name}' not available for {self.vm_name}.")
        return None

    def _check_cpu_usage(self, metrics_data):
        """Checks CPU usage against a threshold."""
        threshold = self.config.getfloat('cpu_threshold', 90.0)
        cpu_percent = self._get_latest_metric_value(metrics_data, "Percentage CPU")
        if cpu_percent is not None:
            logging.debug(f"  -> CPU Usage: {cpu_percent:.2f}%")
            if cpu_percent >= threshold:
                return f"VM '{self.vm_name}' CPU usage is high: {cpu_percent:.2f}% (Threshold: >{threshold}%)"
        return None

    def _check_memory_usage(self, metrics_data):
        """Checks available memory against a threshold."""
        threshold_mb = self.config.getfloat('memory_threshold_mb', 1024.0)
        available_bytes = self._get_latest_metric_value(metrics_data, "Available Memory Bytes")
        if available_bytes is not None:
            available_mb = available_bytes / (1024 * 1024)
            logging.debug(f"  -> Available Memory: {available_mb:.2f} MB")
            if available_mb <= threshold_mb:
                return f"VM '{self.vm_name}' available memory is low: {available_mb:.2f} MB (Threshold: <{threshold_mb} MB)"
        return None

