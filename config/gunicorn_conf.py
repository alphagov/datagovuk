import os

from prometheus_client import CollectorRegistry, multiprocess, start_http_server


def on_starting(server):
    """
    Runs once when the Gunicorn master process boots up.
    """
    metrics_port = int(os.getenv("METRICS_PORT", "9394"))

    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    start_http_server(metrics_port, registry=registry)


# Gunicorn hook to clean up Prometheus metrics when a worker exits
def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
