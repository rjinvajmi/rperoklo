import pytest

from faststream import TestApp, context
from faststream.kafka import TestKafkaBroker
from tests.marks import pydantic_v2
from tests.mocks import mock_pydantic_settings_env


@pydantic_v2
@pytest.mark.asyncio
async def test():
    with mock_pydantic_settings_env({"host": "localhost"}):
        from docs.docs_src.getting_started.cli.kafka_context import app, broker

        async with TestKafkaBroker(broker), TestApp(app, {"env": ""}):
            assert context.get("settings").host == "localhost"
