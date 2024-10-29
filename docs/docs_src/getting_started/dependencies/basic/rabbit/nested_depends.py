from faststream import FastStream, Depends
from faststream.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = FastStream(broker)

def another_dependency():
    return 1

def simple_dependency(b: int = Depends(another_dependency)): # (1)
    return b * 2

@broker.subscriber("test")
async def handler(
    body: dict,
    a: int = Depends(another_dependency),
    b: int = Depends(simple_dependency)):
    assert (a + b) == 3
