import asyncio
from unittest.mock import Mock, patch

import pytest
from nats.aio.msg import Msg

from faststream.exceptions import AckMessage
from faststream.nats import ConsumerConfig, JStream, NatsBroker, PullSub
from faststream.nats.annotations import NatsMessage
from tests.brokers.base.consume import BrokerRealConsumeTestcase
from tests.tools import spy_decorator


@pytest.mark.nats
class TestConsume(BrokerRealConsumeTestcase):
    def get_broker(self, apply_types: bool = False) -> NatsBroker:
        return NatsBroker(apply_types=apply_types)

    async def test_consume_js(
        self,
        queue: str,
        stream: JStream,
        event: asyncio.Event,
    ):
        consume_broker = self.get_broker()

        @consume_broker.subscriber(queue, stream=stream)
        def subscriber(m):
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()
            await asyncio.wait(
                (
                    asyncio.create_task(br.publish("hello", queue, stream=stream.name)),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()

    async def test_consume_with_filter(
        self,
        queue,
        mock: Mock,
        event: asyncio.Event,
    ):
        consume_broker = self.get_broker()

        @consume_broker.subscriber(
            config=ConsumerConfig(filter_subjects=[f"{queue}.a"]),
            stream=JStream(queue, subjects=[f"{queue}.*"]),
        )
        def subscriber(m):
            mock(m)
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()
            await asyncio.wait(
                (
                    asyncio.create_task(br.publish(2, f"{queue}.a")),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        mock.assert_called_once_with(2)

    async def test_consume_pull(
        self,
        queue: str,
        stream: JStream,
        event: asyncio.Event,
        mock,
    ):
        consume_broker = self.get_broker()

        @consume_broker.subscriber(
            queue,
            stream=stream,
            pull_sub=PullSub(1),
        )
        def subscriber(m):
            mock(m)
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            await asyncio.wait(
                (
                    asyncio.create_task(br.publish("hello", queue)),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

            assert event.is_set()
            mock.assert_called_once_with("hello")

    async def test_consume_batch(
        self,
        queue: str,
        stream: JStream,
        event: asyncio.Event,
        mock,
    ):
        consume_broker = self.get_broker()

        @consume_broker.subscriber(
            queue,
            stream=stream,
            pull_sub=PullSub(1, batch=True),
        )
        def subscriber(m):
            mock(m)
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            await asyncio.wait(
                (
                    asyncio.create_task(br.publish(b"hello", queue)),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

            assert event.is_set()
            mock.assert_called_once_with([b"hello"])

    async def test_consume_ack(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, stream=stream)
        async def handler(msg: NatsMessage):
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            with patch.object(Msg, "ack", spy_decorator(Msg.ack)) as m:
                await asyncio.wait(
                    (
                        asyncio.create_task(br.publish("hello", queue)),
                        asyncio.create_task(event.wait()),
                    ),
                    timeout=3,
                )
                m.mock.assert_called_once()

        assert event.is_set()

    async def test_core_consume_no_ack(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, no_ack=True)
        async def handler(msg: NatsMessage):
            if not msg.raw_message._ackd:
                event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            await asyncio.wait(
                (
                    asyncio.create_task(br.publish("hello", queue)),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()

    async def test_consume_ack_manual(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, stream=stream)
        async def handler(msg: NatsMessage):
            await msg.ack()
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            with patch.object(Msg, "ack", spy_decorator(Msg.ack)) as m:
                await asyncio.wait(
                    (
                        asyncio.create_task(br.publish("hello", queue)),
                        asyncio.create_task(event.wait()),
                    ),
                    timeout=3,
                )
                m.mock.assert_called_once()

        assert event.is_set()

    async def test_consume_ack_raise(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, stream=stream)
        async def handler(msg: NatsMessage):
            event.set()
            raise AckMessage()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            with patch.object(Msg, "ack", spy_decorator(Msg.ack)) as m:
                await asyncio.wait(
                    (
                        asyncio.create_task(br.publish("hello", queue)),
                        asyncio.create_task(event.wait()),
                    ),
                    timeout=3,
                )
                m.mock.assert_called_once()

        assert event.is_set()

    async def test_nack(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, stream=stream)
        async def handler(msg: NatsMessage):
            await msg.nack()
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            with patch.object(Msg, "nak", spy_decorator(Msg.nak)) as m:
                await asyncio.wait(
                    (
                        asyncio.create_task(br.publish("hello", queue)),
                        asyncio.create_task(event.wait()),
                    ),
                    timeout=3,
                )
                m.mock.assert_called_once()

        assert event.is_set()

    async def test_consume_no_ack(
        self,
        queue: str,
        event: asyncio.Event,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, no_ack=True)
        async def handler(msg: NatsMessage):
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()

            with patch.object(Msg, "ack", spy_decorator(Msg.ack)) as m:
                await asyncio.wait(
                    (
                        asyncio.create_task(br.publish("hello", queue)),
                        asyncio.create_task(event.wait()),
                    ),
                    timeout=3,
                )
                m.mock.assert_not_called()

            assert event.is_set()

    async def test_consume_batch_headers(
        self,
        queue: str,
        stream: JStream,
        event: asyncio.Event,
        mock,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(
            queue,
            stream=stream,
            pull_sub=PullSub(1, batch=True),
        )
        def subscriber(m, msg: NatsMessage):
            check = all(
                (
                    msg.headers,
                    [msg.headers] == msg.batch_headers,
                    msg.headers.get("custom") == "1",
                )
            )
            mock(check)
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()
            await asyncio.wait(
                (
                    asyncio.create_task(br.publish("", queue, headers={"custom": "1"})),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        mock.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_consume_kv(
        self,
        queue: str,
        event: asyncio.Event,
        mock,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, kv_watch=queue + "1")
        async def handler(m):
            mock(m)
            event.set()

        async with self.patch_broker(consume_broker) as br:
            await br.start()
            bucket = await br.key_value(queue + "1")

            await asyncio.wait(
                (
                    asyncio.create_task(
                        bucket.put(
                            queue,
                            b"world",
                        )
                    ),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        mock.assert_called_with(b"world")

    @pytest.mark.asyncio
    async def test_consume_os(
        self,
        queue: str,
        event: asyncio.Event,
        mock,
    ):
        consume_broker = self.get_broker(apply_types=True)

        @consume_broker.subscriber(queue, obj_watch=True)
        async def handler(filename: str):
            event.set()
            mock(filename)

        async with self.patch_broker(consume_broker) as br:
            await br.start()
            bucket = await br.object_storage(queue)

            await asyncio.wait(
                (
                    asyncio.create_task(
                        bucket.put(
                            "hello",
                            b"world",
                        )
                    ),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        mock.assert_called_once_with("hello")

    async def test_get_one_js(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(queue, stream=stream)

        async with self.patch_broker(broker) as br:
            await br.start()

            message = None

            async def consume():
                nonlocal message
                message = await subscriber.get_one(timeout=5)

            async def publish():
                await br.publish("test_message", queue, stream=stream.name)

            await asyncio.wait(
                (
                    asyncio.create_task(consume()),
                    asyncio.create_task(publish()),
                ),
                timeout=10,
            )

            assert message is not None
            assert await message.decode() == "test_message"

    async def test_get_one_timeout_js(
        self,
        queue: str,
        stream: JStream,
        mock,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(queue, stream=stream)

        async with self.patch_broker(broker) as br:
            await br.start()

            mock(await subscriber.get_one(timeout=1e-24))
            mock.assert_called_once_with(None)

    async def test_get_one_pull(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(
            queue,
            stream=stream,
            pull_sub=PullSub(1),
        )

        async with self.patch_broker(broker) as br:
            await br.start()

            message = None

            async def consume():
                nonlocal message
                message = await subscriber.get_one(timeout=5)

            async def publish():
                await br.publish("test_message", queue)

            await asyncio.wait(
                (
                    asyncio.create_task(consume()),
                    asyncio.create_task(publish()),
                ),
                timeout=10,
            )

            assert message is not None
            assert await message.decode() == "test_message"

    async def test_get_one_pull_timeout(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
        mock: Mock,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(
            queue,
            stream=stream,
            pull_sub=PullSub(1),
        )

        async with self.patch_broker(broker) as br:
            await br.start()

            mock(await subscriber.get_one(timeout=1e-24))
            mock.assert_called_once_with(None)

    async def test_get_one_batch(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(
            queue,
            stream=stream,
            pull_sub=PullSub(1, batch=True),
        )

        async with self.patch_broker(broker) as br:
            await br.start()

            message = None

            async def consume():
                nonlocal message
                message = await subscriber.get_one(timeout=5)

            async def publish():
                await br.publish("test_message", queue)

            await asyncio.wait(
                (
                    asyncio.create_task(consume()),
                    asyncio.create_task(publish()),
                ),
                timeout=10,
            )

            assert message is not None
            assert await message.decode() == ["test_message"]

    async def test_get_one_batch_timeout(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
        mock: Mock,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(
            queue,
            stream=stream,
            pull_sub=PullSub(1, batch=True),
        )

        async with self.patch_broker(broker) as br:
            await br.start()

            mock(await subscriber.get_one(timeout=1e-24))
            mock.assert_called_once_with(None)

    async def test_get_one_with_filter(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(
            config=ConsumerConfig(filter_subjects=[f"{queue}.a"]),
            stream=JStream(queue, subjects=[f"{queue}.*"]),
        )

        async with self.patch_broker(broker) as br:
            await br.start()

            message = None

            async def consume():
                nonlocal message
                message = await subscriber.get_one(timeout=5)

            async def publish():
                await br.publish("test_message", f"{queue}.a")

            await asyncio.wait(
                (
                    asyncio.create_task(publish()),
                    asyncio.create_task(consume()),
                ),
                timeout=10,
            )

            assert message is not None
            assert await message.decode() == "test_message"

    async def test_get_one_kv(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(queue, kv_watch=queue + "1")

        async with self.patch_broker(broker) as br:
            await br.start()
            bucket = await br.key_value(queue + "1")

            message = None

            async def consume():
                nonlocal message
                message = await subscriber.get_one(timeout=5)

            async def publish():
                await bucket.put(queue, b"test_message")

            await asyncio.wait(
                (
                    asyncio.create_task(consume()),
                    asyncio.create_task(publish()),
                ),
                timeout=10,
            )

            assert message is not None
            assert await message.decode() == b"test_message"

    async def test_get_one_kv_timeout(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
        mock: Mock,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(queue, kv_watch=queue + "1")

        async with self.patch_broker(broker) as br:
            await br.start()

            mock(await subscriber.get_one(timeout=1e-24))
            mock.assert_called_once_with(None)

    async def test_get_one_os(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(queue, obj_watch=True)

        async with self.patch_broker(broker) as br:
            await br.start()
            bucket = await br.object_storage(queue)

            new_object_id = None

            async def consume():
                nonlocal new_object_id
                new_object_event = await subscriber.get_one(timeout=5)
                new_object_id = await new_object_event.decode()

            async def publish():
                await bucket.put(queue, b"test_message")

            await asyncio.wait(
                (
                    asyncio.create_task(consume()),
                    asyncio.create_task(publish()),
                ),
                timeout=10,
            )

            new_object = await bucket.get(new_object_id)
            assert new_object.data == b"test_message"

    async def test_get_one_os_timeout(
        self,
        queue: str,
        event: asyncio.Event,
        stream: JStream,
        mock: Mock,
    ):
        broker = self.get_broker(apply_types=True)
        subscriber = broker.subscriber(queue, obj_watch=True)

        async with self.patch_broker(broker) as br:
            await br.start()

            mock(await subscriber.get_one(timeout=1e-24))
            mock.assert_called_once_with(None)
