import asyncio
from unittest.mock import Mock

import pytest
from prometheus_client import CollectorRegistry

from faststream import Context
from faststream.kafka import KafkaBroker
from faststream.kafka.prometheus.middleware import KafkaPrometheusMiddleware
from tests.brokers.kafka.test_consume import TestConsume
from tests.brokers.kafka.test_publish import TestPublish
from tests.prometheus.basic import LocalPrometheusTestcase


@pytest.mark.kafka
class TestPrometheus(LocalPrometheusTestcase):
    def get_broker(self, apply_types=False, **kwargs):
        return KafkaBroker(apply_types=apply_types, **kwargs)

    def get_middleware(self, **kwargs):
        return KafkaPrometheusMiddleware(**kwargs)

    async def test_metrics_batch(
        self,
        event: asyncio.Event,
        queue: str,
    ):
        middleware = self.get_middleware(registry=CollectorRegistry())
        metrics_manager_mock = Mock()
        middleware._metrics_manager = metrics_manager_mock

        broker = self.get_broker(apply_types=True, middlewares=(middleware,))

        args, kwargs = self.get_subscriber_params(queue, batch=True)
        message = None

        @broker.subscriber(*args, **kwargs)
        async def handler(m=Context("message")):
            event.set()

            nonlocal message
            message = m

        async with broker:
            await broker.start()
            tasks = (
                asyncio.create_task(
                    broker.publish_batch("hello", "world", topic=queue)
                ),
                asyncio.create_task(event.wait()),
            )
            await asyncio.wait(tasks, timeout=self.timeout)

        assert event.is_set()
        self.assert_consume_metrics(
            metrics_manager=metrics_manager_mock, message=message, exception_class=None
        )
        self.assert_publish_metrics(metrics_manager=metrics_manager_mock)


@pytest.mark.kafka
class TestPublishWithPrometheus(TestPublish):
    def get_broker(
        self,
        apply_types: bool = False,
        **kwargs,
    ):
        return KafkaBroker(
            middlewares=(KafkaPrometheusMiddleware(registry=CollectorRegistry()),),
            apply_types=apply_types,
            **kwargs,
        )


@pytest.mark.kafka
class TestConsumeWithPrometheus(TestConsume):
    def get_broker(self, apply_types: bool = False, **kwargs):
        return KafkaBroker(
            middlewares=(KafkaPrometheusMiddleware(registry=CollectorRegistry()),),
            apply_types=apply_types,
            **kwargs,
        )
