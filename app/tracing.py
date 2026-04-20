from __future__ import annotations

import os
from typing import Any

try:
    from langfuse.decorators import observe, langfuse_context
    from langfuse.callback import CallbackHandler
    from langfuse import Langfuse as _Langfuse
    _HAS_LANGFUSE = True
except Exception:  # pragma: no cover
    _HAS_LANGFUSE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

        def flush(self) -> None:
            return None

    langfuse_context = _DummyContext()
    CallbackHandler = None
    _Langfuse = None


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


_cached_callback = None
_cached_client = None


def get_langfuse_client():
    """Trả về Langfuse client v2 (dùng để flush)."""
    global _cached_client
    if not tracing_enabled() or not _HAS_LANGFUSE or _Langfuse is None:
        return None
    if _cached_client is None:
        host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASEURL")
        _cached_client = _Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=host,
        )
    return _cached_client


def get_langfuse_callback():
    """Trả về LangChain CallbackHandler cho LangGraph."""
    global _cached_callback
    if not tracing_enabled() or not _HAS_LANGFUSE or CallbackHandler is None:
        return None
    if _cached_callback is None:
        host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASEURL")
        _cached_callback = CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=host,
        )
    return _cached_callback
