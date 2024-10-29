from fastapi import Depends, FastAPI
from pydantic import BaseModel

from faststream.redis.fastapi import RedisRouter, Logger

router = RedisRouter("redis://localhost:6379")

class Incoming(BaseModel):
    m: dict

def call():
    return True

@router.subscriber("test")
@router.publisher("response")
async def hello(m: Incoming, logger: Logger, d=Depends(call)):
    logger.info(m)
    return {"response": "Hello, Redis!"}

@router.get("/")
async def hello_http():
    return "Hello, HTTP!"

app = FastAPI()
app.include_router(router)
