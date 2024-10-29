from typing import TYPE_CHECKING, Any, List, Optional, cast

from opentelemetry import baggage, context
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from typing_extensions import Self

if TYPE_CHECKING:
    from faststream.broker.message import StreamMessage
    from faststream.types import AnyDict

_BAGGAGE_PROPAGATOR = W3CBaggagePropagator()


class Baggage:
    __slots__ = ("_baggage", "_batch_baggage")

    def __init__(
        self, payload: "AnyDict", batch_payload: Optional[List["AnyDict"]] = None
    ) -> None:
        self._baggage = dict(payload)
        self._batch_baggage = [dict(b) for b in batch_payload] if batch_payload else []

    def get_all(self) -> "AnyDict":
        """Get a copy of the current baggage."""
        return self._baggage.copy()

    def get_all_batch(self) -> List["AnyDict"]:
        """Get a copy of all batch baggage if exists."""
        return self._batch_baggage.copy()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the baggage by key."""
        return self._baggage.get(key)

    def remove(self, key: str) -> None:
        """Remove a baggage item by key."""
        self._baggage.pop(key, None)

    def set(self, key: str, value: Any) -> None:
        """Set a key-value pair in the baggage."""
        self._baggage[key] = value

    def clear(self) -> None:
        """Clear the current baggage."""
        self._baggage.clear()

    def to_headers(self, headers: Optional["AnyDict"] = None) -> "AnyDict":
        """Convert baggage items to headers format for propagation."""
        current_context = context.get_current()
        if headers is None:
            headers = {}

        for k, v in self._baggage.items():
            current_context = baggage.set_baggage(k, v, context=current_context)

        _BAGGAGE_PROPAGATOR.inject(headers, current_context)
        return headers

    @classmethod
    def from_msg(cls, msg: "StreamMessage[Any]") -> Self:
        """Create a Baggage instance from a StreamMessage."""
        if len(msg.batch_headers) <= 1:
            payload = baggage.get_all(_BAGGAGE_PROPAGATOR.extract(msg.headers))
            return cls(cast("AnyDict", payload))

        cumulative_baggage: AnyDict = {}
        batch_baggage: List[AnyDict] = []

        for headers in msg.batch_headers:
            payload = baggage.get_all(_BAGGAGE_PROPAGATOR.extract(headers))
            cumulative_baggage.update(payload)
            batch_baggage.append(cast("AnyDict", payload))

        return cls(cumulative_baggage, batch_baggage)

    def __repr__(self) -> str:
        return self._baggage.__repr__()
