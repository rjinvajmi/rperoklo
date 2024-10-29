from faststream import FastStream
from faststream.asyncapi.generate import get_app_schema
from faststream.confluent import KafkaBroker, KafkaPublisher, KafkaRoute, KafkaRouter
from tests.asyncapi.base.arguments import ArgumentsTestcase
from tests.asyncapi.base.publisher import PublisherTestcase
from tests.asyncapi.base.router import RouterTestcase


class TestRouter(RouterTestcase):
    broker_class = KafkaBroker
    router_class = KafkaRouter
    route_class = KafkaRoute
    publisher_class = KafkaPublisher

    def test_prefix(self):
        broker = self.broker_class()

        router = self.router_class(prefix="test_")

        @router.subscriber("test")
        async def handle(msg): ...

        broker.include_router(router)

        schema = get_app_schema(FastStream(broker)).to_jsonable()

        assert schema == {
            "asyncapi": "2.6.0",
            "defaultContentType": "application/json",
            "info": {"title": "FastStream", "version": "0.1.0", "description": ""},
            "servers": {
                "development": {
                    "url": "localhost",
                    "protocol": "kafka",
                    "protocolVersion": "auto",
                }
            },
            "channels": {
                "test_test:Handle": {
                    "servers": ["development"],
                    "bindings": {
                        "kafka": {"topic": "test_test", "bindingVersion": "0.4.0"}
                    },
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
                        "title": "test_test:Handle:Message",
                        "correlationId": {
                            "location": "$message.header#/correlation_id"
                        },
                        "payload": {
                            "$ref": "#/components/schemas/Handle:Message:Payload"
                        },
                    }
                },
                "schemas": {
                    "Handle:Message:Payload": {"title": "Handle:Message:Payload"}
                },
            },
        }


class TestRouterArguments(ArgumentsTestcase):
    broker_class = KafkaRouter

    def build_app(self, router):
        broker = KafkaBroker()
        broker.include_router(router)
        return FastStream(broker)


class TestRouterPublisher(PublisherTestcase):
    broker_class = KafkaRouter

    def build_app(self, router):
        broker = KafkaBroker()
        broker.include_router(router)
        return FastStream(broker)
