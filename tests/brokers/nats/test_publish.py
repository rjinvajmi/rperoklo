import asyncio
from unittest.mock import Mock

import pytest

from faststream import Context
from faststream.nats import NatsBroker, NatsResponse
from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.nats
class TestPublish(BrokerPublishTestcase):
    """Test publish method of NATS broker."""

    def get_broker(self, apply_types: bool = False) -> NatsBroker:
        return NatsBroker(apply_types=apply_types)

    @pytest.mark.asyncio
    async def test_response(
        self,
        queue: str,
        event: asyncio.Event,
        mock: Mock,
    ):
        pub_broker = self.get_broker(apply_types=True)

        @pub_broker.subscriber(queue)
        @pub_broker.publisher(queue + "1")
        async def handle():
            return NatsResponse(1, correlation_id="1")

        @pub_broker.subscriber(queue + "1")
        async def handle_next(msg=Context("message")):
            mock(
                body=msg.body,
                correlation_id=msg.correlation_id,
            )
            event.set()

        async with self.patch_broker(pub_broker) as br:
            await br.start()

            await asyncio.wait(
                (
                    asyncio.create_task(br.publish("", queue, correlation_id="wrong")),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        mock.assert_called_once_with(
            body=b"1",
            correlation_id="1",
        )

    @pytest.mark.asyncio
    async def test_response_for_rpc(
        self,
        queue: str,
        event: asyncio.Event,
    ):
        pub_broker = self.get_broker(apply_types=True)

        @pub_broker.subscriber(queue)
        async def handle():
            return NatsResponse("Hi!", correlation_id="1")

        async with self.patch_broker(pub_broker) as br:
            await br.start()

            response = await asyncio.wait_for(
                br.publish("", queue, rpc=True),
                timeout=3,
            )

            assert response == "Hi!", response
