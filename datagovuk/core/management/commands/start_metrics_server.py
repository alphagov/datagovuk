import signal
import threading

from django.conf import settings
from django.core.management.base import BaseCommand
from prometheus_client import start_http_server


class Command(BaseCommand):
    """
    Django management command to start the Prometheus metrics HTTP server
    on an internal-only port, with graceful shutdown support.
    """

    help = "Start the Prometheus metrics HTTP server on an internal-only port"

    def handle(self, *args, **options):
        port = settings.PROMETHEUS_METRICS_PORT
        self.stdout.write(f"Starting metrics server on port {port}")
        server, server_thread = start_http_server(port)
        shutdown_event = threading.Event()
        signal.signal(signal.SIGTERM, lambda *_: shutdown_event.set())
        try:
            shutdown_event.wait()
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join()
            self.stdout.write("Metrics server stopped")
