from prometheus_client import multiprocess


# Gunicorn hook to clean up Prometheus metrics when a worker exits
def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
