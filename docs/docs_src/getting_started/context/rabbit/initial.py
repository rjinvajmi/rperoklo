from faststream import Context
from faststream.rabbit import RabbitBroker

broker = RabbitBroker()

@broker.subscriber("test-queue")
async def handle(
    msg: str,
    collector: list[str] = Context(initial=list),
):
    collector.append(msg)
