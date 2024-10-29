---
# 0.5 - API
# 2 - Release
# 3 - Contributing
# 5 - Template Page
# 10 - Default
search:
  boost: 10
---

# Access to Message Information

As you know, **FastStream** serializes a message body and provides you access to it through function arguments. But sometimes you need to access message_id, headers, or other meta-information.

## Message Access

You can get it in a simple way: just access the message object in the [Context](../getting-started/context/existed.md){.internal-link}.

It contains the required information such as:

{! includes/message/attrs.md !}

It is a **FastStream** wrapper around a native broker library message (`nats.aio.msg.Msg` in the *NATS*' case) that you can access with `raw_message`.

```python hl_lines="1 6"
from faststream.nats import NatsMessage

@broker.subscriber("test")
async def base_handler(
    body: str,
    msg: NatsMessage,
):
    print(msg.correlation_id)
```

Also, if you can't find the information you require, you can get access directly to the wrapped `nats.aio.msg.Msg`, which contains complete message information.

```python hl_lines="6"
from nats.aio.msg import Msg
from faststream.nats import NatsMessage

@broker.subscriber("test")
async def base_handler(body: str, msg: NatsMessage):
    raw: Msg = msg.raw_message
    print(raw)
```

## Message Fields Access

But in most cases, you don't need all message fields; you need to access some of them. You can use [Context Fields access](../getting-started/context/fields.md){.internal-link} feature for this reason.

For example, you can access the `correlation_id` like this:

```python hl_lines="6"
from faststream import Context

@broker.subscriber("test")
async def base_handler(
    body: str,
    cor_id: str = Context("message.correlation_id"),
):
    print(cor_id)
```

Or even directly from the raw message:

```python hl_lines="6"
from faststream import Context

@broker.subscriber("test")
async def base_handler(
    body: str,
    cor_id: str = Context("message.raw_message.correlation_id"),
):
    print(cor_id)
```

But this code is too long to reuse everywhere. In this case, you can use a Python [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated){.external-link target="_blank"} feature:

{! includes/message/annotated.md !}

{! includes/message/headers.md !}

## Subject Pattern Access

As you know, **NATS** allows you to use a pattern like this `#!python "logs.*"` to subscriber to subjects. Getting access to the real `*` value is an often-used scenario, and **FastStream** provide it to you with the `Path` object (which is a shortcut to `#!python Context("message.path.*")`).

To use it, you just need to replace your `*` with `{variable-name}` and use `Path` as a regular `Context` object:

```python hl_lines="3 6"
from faststream import Path

@broker.subscriber("logs.{level}")
async def base_handler(
    body: str,
    level: str = Path(),
):
    ...
```
