from faststream.asyncapi.generate import get_app_schema
from faststream.redis import RedisBroker, StreamSub
from tests.asyncapi.base.arguments import ArgumentsTestcase


class TestArguments(ArgumentsTestcase):
    broker_class = RedisBroker

    def test_channel_subscriber(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg): ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()
        key = tuple(schema["channels"].keys())[0]  # noqa: RUF015

        assert schema["channels"][key]["bindings"] == {
            "redis": {
                "bindingVersion": "custom",
                "channel": "test",
                "method": "subscribe",
            }
        }

    def test_channel_pattern_subscriber(self):
        broker = self.broker_class()

        @broker.subscriber("test.{path}")
        async def handle(msg): ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()
        key = tuple(schema["channels"].keys())[0]  # noqa: RUF015

        assert schema["channels"][key]["bindings"] == {
            "redis": {
                "bindingVersion": "custom",
                "channel": "test.*",
                "method": "psubscribe",
            }
        }

    def test_list_subscriber(self):
        broker = self.broker_class()

        @broker.subscriber(list="test")
        async def handle(msg): ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()
        key = tuple(schema["channels"].keys())[0]  # noqa: RUF015

        assert schema["channels"][key]["bindings"] == {
            "redis": {"bindingVersion": "custom", "channel": "test", "method": "lpop"}
        }

    def test_stream_subscriber(self):
        broker = self.broker_class()

        @broker.subscriber(stream="test")
        async def handle(msg): ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()
        key = tuple(schema["channels"].keys())[0]  # noqa: RUF015

        assert schema["channels"][key]["bindings"] == {
            "redis": {"bindingVersion": "custom", "channel": "test", "method": "xread"}
        }

    def test_stream_group_subscriber(self):
        broker = self.broker_class()

        @broker.subscriber(stream=StreamSub("test", group="group", consumer="consumer"))
        async def handle(msg): ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()
        key = tuple(schema["channels"].keys())[0]  # noqa: RUF015

        assert schema["channels"][key]["bindings"] == {
            "redis": {
                "bindingVersion": "custom",
                "channel": "test",
                "consumer_name": "consumer",
                "group_name": "group",
                "method": "xreadgroup",
            }
        }
