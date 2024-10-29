from faststream import FastStream, Depends
from faststream.kafka import KafkaBroker

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)

def simple_dependency():
    return 1

@broker.subscriber("test")
async def handler(body: dict, d: int = Depends(simple_dependency)):
    assert d == 1
