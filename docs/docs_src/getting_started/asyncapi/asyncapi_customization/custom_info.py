from faststream import FastStream
from faststream.kafka import KafkaBroker, KafkaMessage
from faststream.asyncapi.schema import Contact, ExternalDocs, License, Tag

broker = KafkaBroker("localhost:9092")
description="""# Title of the description
This description supports **Markdown** syntax"""
app = FastStream(
    broker,
    title="My App",
    version="1.0.0",
    description=description,
    license=License(name="MIT", url="https://opensource.org/license/mit/"),
    terms_of_service="https://my-terms.com/",
    contact=Contact(name="support", url="https://help.com/"),
)

@broker.publisher("output_data")
@broker.subscriber("input_data")
async def on_input_data(msg):
    # your processing logic
    pass
