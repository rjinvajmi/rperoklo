from faststream import Context
from faststream.nats import NatsBroker

broker = NatsBroker()

@broker.subscriber("test-subject")
async def handle(
    msg: str,
    collector: list[str] = Context(initial=list),
):
    collector.append(msg)
