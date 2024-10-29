from pydantic import Field, NonNegativeInt

from faststream import FastStream
from faststream.confluent import KafkaBroker

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


@broker.subscriber("test-topic-confluent", auto_offset_reset="earliest")
async def handle(
    name: str = Field(
        ..., examples=["John"], description="Registered user name"
    ),
    user_id: NonNegativeInt = Field(
        ..., examples=[1], description="Registered user id"
    ),
):
    assert name == "John"
    assert user_id == 1


@broker.subscriber("test-confluent-wrong-fields", auto_offset_reset="earliest")
async def wrong_handle(
    name: str = Field(
        ..., examples=["John"], description="Registered user name"
    ),
    user_id: NonNegativeInt = Field(
        ..., examples=[1], description="Registered user id"
    ),
):
    assert name == "John"
    assert user_id == 1
