from faststream import Context
from faststream.kafka import KafkaBroker

broker = KafkaBroker()

@broker.subscriber("test-topic")
async def handle(
    msg: str,
    collector: list[str] = Context(initial=list),
):
    collector.append(msg)
