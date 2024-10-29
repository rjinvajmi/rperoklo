from faststream import FastStream
from faststream.asyncapi.generate import get_app_schema
from faststream.asyncapi.schema import Tag
from faststream.rabbit import RabbitBroker


def test_base():
    schema = get_app_schema(
        FastStream(
            RabbitBroker(
                "amqps://localhost",
                port=5673,
                protocol_version="0.9.0",
                description="Test description",
                tags=(Tag(name="some-tag", description="experimental"),),
            )
        )
    ).to_jsonable()

    assert schema == {
        "asyncapi": "2.6.0",
        "channels": {},
        "components": {"messages": {}, "schemas": {}},
        "defaultContentType": "application/json",
        "info": {"description": "", "title": "FastStream", "version": "0.1.0"},
        "servers": {
            "development": {
                "description": "Test description",
                "protocol": "amqps",
                "protocolVersion": "0.9.0",
                "tags": [{"description": "experimental", "name": "some-tag"}],
                "url": "amqps://guest:guest@localhost:5673/",  # pragma: allowlist secret
            }
        },
    }


def test_kwargs():
    broker = RabbitBroker(
        "amqp://guest:guest@localhost:5672/?heartbeat=300",  # pragma: allowlist secret
        host="127.0.0.1",
    )

    assert (
        broker.url
        == "amqp://guest:guest@127.0.0.1:5672/?heartbeat=300"  # pragma: allowlist secret
    )


def test_custom():
    broker = RabbitBroker(
        "amqps://localhost",
        asyncapi_url="amqp://guest:guest@127.0.0.1:5672/vh",  # pragma: allowlist secret
    )

    broker.publisher("test")
    schema = get_app_schema(FastStream(broker)).to_jsonable()

    assert (
        schema
        == {
            "asyncapi": "2.6.0",
            "channels": {
                "test:_:Publisher": {
                    "bindings": {
                        "amqp": {
                            "bindingVersion": "0.2.0",
                            "exchange": {"type": "default", "vhost": "/vh"},
                            "is": "routingKey",
                            "queue": {
                                "autoDelete": False,
                                "durable": False,
                                "exclusive": False,
                                "name": "test",
                                "vhost": "/vh",
                            },
                        }
                    },
                    "publish": {
                        "bindings": {
                            "amqp": {
                                "ack": True,
                                "bindingVersion": "0.2.0",
                                "cc": "test",
                                "deliveryMode": 1,
                                "mandatory": True,
                            }
                        },
                        "message": {
                            "$ref": "#/components/messages/test:_:Publisher:Message"
                        },
                    },
                    "servers": ["development"],
                }
            },
            "components": {
                "messages": {
                    "test:_:Publisher:Message": {
                        "correlationId": {
                            "location": "$message.header#/correlation_id"
                        },
                        "payload": {
                            "$ref": "#/components/schemas/test:_:PublisherPayload"
                        },
                        "title": "test:_:Publisher:Message",
                    }
                },
                "schemas": {"test:_:PublisherPayload": {}},
            },
            "defaultContentType": "application/json",
            "info": {"description": "", "title": "FastStream", "version": "0.1.0"},
            "servers": {
                "development": {
                    "protocol": "amqp",
                    "protocolVersion": "0.9.1",
                    "url": "amqp://guest:guest@127.0.0.1:5672/vh",  # pragma: allowlist secret
                }
            },
        }
    )
