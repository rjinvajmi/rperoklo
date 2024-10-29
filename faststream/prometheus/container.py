from typing import Optional, Sequence

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class MetricsContainer:
    __slots__ = (
        "_registry",
        "_metrics_prefix",
        "received_messages_total",
        "received_messages_size_bytes",
        "received_processed_messages_duration_seconds",
        "received_messages_in_process",
        "received_processed_messages_total",
        "received_processed_messages_exceptions_total",
        "published_messages_total",
        "published_messages_duration_seconds",
        "published_messages_exceptions_total",
    )

    DEFAULT_SIZE_BUCKETS = (
        2.0**4,
        2.0**6,
        2.0**8,
        2.0**10,
        2.0**12,
        2.0**14,
        2.0**16,
        2.0**18,
        2.0**20,
        2.0**22,
        2.0**24,
        float("inf"),
    )

    def __init__(
        self,
        registry: "CollectorRegistry",
        *,
        metrics_prefix: str = "faststream",
        received_messages_size_buckets: Optional[Sequence[float]] = None,
    ):
        self._registry = registry
        self._metrics_prefix = metrics_prefix

        self.received_messages_total = Counter(
            name=f"{metrics_prefix}_received_messages_total",
            documentation="Count of received messages by broker and handler",
            labelnames=["app_name", "broker", "handler"],
            registry=registry,
        )
        self.received_messages_size_bytes = Histogram(
            name=f"{metrics_prefix}_received_messages_size_bytes",
            documentation="Histogram of received messages size in bytes by broker and handler",
            labelnames=["app_name", "broker", "handler"],
            registry=registry,
            buckets=received_messages_size_buckets or self.DEFAULT_SIZE_BUCKETS,
        )
        self.received_messages_in_process = Gauge(
            name=f"{metrics_prefix}_received_messages_in_process",
            documentation="Gauge of received messages in process by broker and handler",
            labelnames=["app_name", "broker", "handler"],
            registry=registry,
        )
        self.received_processed_messages_total = Counter(
            name=f"{metrics_prefix}_received_processed_messages_total",
            documentation="Count of received processed messages by broker, handler and status",
            labelnames=["app_name", "broker", "handler", "status"],
            registry=registry,
        )
        self.received_processed_messages_duration_seconds = Histogram(
            name=f"{metrics_prefix}_received_processed_messages_duration_seconds",
            documentation="Histogram of received processed messages duration in seconds by broker and handler",
            labelnames=["app_name", "broker", "handler"],
            registry=registry,
        )
        self.received_processed_messages_exceptions_total = Counter(
            name=f"{metrics_prefix}_received_processed_messages_exceptions_total",
            documentation="Count of received processed messages exceptions by broker, handler and exception_type",
            labelnames=["app_name", "broker", "handler", "exception_type"],
            registry=registry,
        )
        self.published_messages_total = Counter(
            name=f"{metrics_prefix}_published_messages_total",
            documentation="Count of published messages by destination and status",
            labelnames=["app_name", "broker", "destination", "status"],
            registry=registry,
        )
        self.published_messages_duration_seconds = Histogram(
            name=f"{metrics_prefix}_published_messages_duration_seconds",
            documentation="Histogram of published messages duration in seconds by broker and destination",
            labelnames=["app_name", "broker", "destination"],
            registry=registry,
        )
        self.published_messages_exceptions_total = Counter(
            name=f"{metrics_prefix}_published_messages_exceptions_total",
            documentation="Count of published messages exceptions by broker, destination and exception_type",
            labelnames=["app_name", "broker", "destination", "exception_type"],
            registry=registry,
        )
