import json
import os
import sys
from importlib.metadata import version as get_version
from typing import Any, Callable, Dict, Mapping, Optional, Type, TypeVar, Union

from fast_depends._compat import PYDANTIC_V2 as PYDANTIC_V2
from fast_depends._compat import (  # type: ignore[attr-defined]
    PYDANTIC_VERSION as PYDANTIC_VERSION,
)
from pydantic import BaseModel as BaseModel

from faststream.types import AnyDict

IS_WINDOWS = (
    sys.platform == "win32" or sys.platform == "cygwin" or sys.platform == "msys"
)


ModelVar = TypeVar("ModelVar", bound=BaseModel)


def is_test_env() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST"))


json_dumps: Callable[..., bytes]
orjson: Any
ujson: Any

try:
    import orjson  # type: ignore[no-redef]
except ImportError:
    orjson = None

try:
    import ujson
except ImportError:
    ujson = None

if orjson:
    json_loads = orjson.loads
    json_dumps = orjson.dumps

elif ujson:
    json_loads = ujson.loads

    def json_dumps(*a: Any, **kw: Any) -> bytes:
        return ujson.dumps(*a, **kw).encode()  # type: ignore

else:
    json_loads = json.loads

    def json_dumps(*a: Any, **kw: Any) -> bytes:
        return json.dumps(*a, **kw).encode()


JsonSchemaValue = Mapping[str, Any]

if PYDANTIC_V2:
    if PYDANTIC_VERSION >= "2.4.0":
        from pydantic.annotated_handlers import (
            GetJsonSchemaHandler as GetJsonSchemaHandler,
        )
        from pydantic_core.core_schema import (
            with_info_plain_validator_function as with_info_plain_validator_function,
        )
    else:
        from pydantic._internal._annotated_handlers import (  # type: ignore[no-redef]
            GetJsonSchemaHandler as GetJsonSchemaHandler,
        )
        from pydantic_core.core_schema import (
            general_plain_validator_function as with_info_plain_validator_function,
        )

    from pydantic.fields import FieldInfo as FieldInfo
    from pydantic_core import CoreSchema as CoreSchema
    from pydantic_core import PydanticUndefined as PydanticUndefined
    from pydantic_core import to_jsonable_python

    SCHEMA_FIELD = "json_schema_extra"
    DEF_KEY = "$defs"

    def model_to_jsonable(
        model: BaseModel,
        **kwargs: Any,
    ) -> Any:
        return to_jsonable_python(model, **kwargs)

    def dump_json(data: Any) -> bytes:
        return json_dumps(model_to_jsonable(data))

    def get_model_fields(model: Type[BaseModel]) -> Dict[str, Any]:
        return model.model_fields

    def model_to_json(model: BaseModel, **kwargs: Any) -> str:
        return model.model_dump_json(**kwargs)

    def model_parse(
        model: Type[ModelVar], data: Union[str, bytes], **kwargs: Any
    ) -> ModelVar:
        return model.model_validate_json(data, **kwargs)

    def model_schema(model: Type[BaseModel], **kwargs: Any) -> AnyDict:
        return model.model_json_schema(**kwargs)

else:
    from pydantic.fields import FieldInfo as FieldInfo
    from pydantic.json import pydantic_encoder

    GetJsonSchemaHandler = Any  # type: ignore[assignment,misc]
    CoreSchema = Any  # type: ignore[assignment,misc]

    SCHEMA_FIELD = "schema_extra"
    DEF_KEY = "definitions"

    PydanticUndefined = Ellipsis  # type: ignore[assignment]

    def dump_json(data: Any) -> bytes:
        return json_dumps(data, default=pydantic_encoder)

    def get_model_fields(model: Type[BaseModel]) -> Dict[str, Any]:
        return model.__fields__  # type: ignore[return-value]

    def model_to_json(model: BaseModel, **kwargs: Any) -> str:
        return model.json(**kwargs)

    def model_parse(
        model: Type[ModelVar], data: Union[str, bytes], **kwargs: Any
    ) -> ModelVar:
        return model.parse_raw(data, **kwargs)

    def model_schema(model: Type[BaseModel], **kwargs: Any) -> AnyDict:
        return model.schema(**kwargs)

    def model_to_jsonable(
        model: BaseModel,
        **kwargs: Any,
    ) -> Any:
        return json_loads(model.json(**kwargs))

    # TODO: pydantic types misc
    def with_info_plain_validator_function(  # type: ignore[misc]
        function: Callable[..., Any],
        *,
        ref: Optional[str] = None,
        metadata: Any = None,
        serialization: Any = None,
    ) -> JsonSchemaValue:
        return {}


anyio_major = int(get_version("anyio").split(".")[0])
ANYIO_V3 = anyio_major == 3


if ANYIO_V3:
    from anyio import ExceptionGroup as ExceptionGroup  # type: ignore[attr-defined]
else:
    if sys.version_info < (3, 11):
        from exceptiongroup import (
            ExceptionGroup as ExceptionGroup,
        )
    else:
        ExceptionGroup = ExceptionGroup
