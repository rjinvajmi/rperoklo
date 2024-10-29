from faststream import FastStream
from faststream.asyncapi.generate import get_app_schema
from faststream.redis import RedisBroker, RedisPublisher, RedisRoute, RedisRouter
from tests.asyncapi.base.arguments import ArgumentsTestcase
from tests.asyncapi.base.publisher import PublisherTestcase
from tests.asyncapi.base.router import RouterTestcase


class TestRouter(RouterTestcase):
    broker_class = RedisBroker
    router_class = RedisRouter
    route_class = RedisRoute
    publisher_class = RedisPublisher

    def test_prefix(self):
        broker = self.broker_class()

        router = self.router_class(prefix="test_")

        @router.subscriber("test")
        async def handle(msg): ...

        broker.include_router(router)

        schema = get_app_schema(FastStream(broker)).to_jsonable()

        assert schema == {
            "asyncapi": "2.6.0",
            "channels": {
                "test_test:Handle": {
                    "bindings": {
                        "redis": {
                            "bindingVersion": "custom",
                            "channel": "test_test",
                            "method": "subscribe",
                        }
                    },
                    "servers": ["development"],
                    "subscribe": {
                        "message": {
                            "$ref": "#/components/messages/test_test:Handle:Message"
                        }
                    },
                }
            },
            "components": {
                "messages": {
                    "test_test:Handle:Message": {
                        "correlationId": {
                            "location": "$message.header#/correlation_id"
                        },
                        "payload": {
                            "$ref": "#/components/schemas/Handle:Message:Payload"
                        },
                        "title": "test_test:Handle:Message",
                    }
                },
                "schemas": {
                    "Handle:Message:Payload": {"title": "Handle:Message:Payload"}
                },
            },
            "defaultContentType": "application/json",
            "info": {"description": "", "title": "FastStream", "version": "0.1.0"},
            "servers": {
                "development": {
                    "protocol": "redis",
                    "protocolVersion": "custom",
                    "url": "redis://localhost:6379",
                }
            },
        }


class TestRouterArguments(ArgumentsTestcase):
    broker_class = RedisRouter

    def build_app(self, router):
        broker = RedisBroker()
        broker.include_router(router)
        return FastStream(broker)


class TestRouterPublisher(PublisherTestcase):
    broker_class = RedisRouter

    def build_app(self, router):
        broker = RedisBroker()
        broker.include_router(router)
        return FastStream(broker)
