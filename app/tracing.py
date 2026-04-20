from __future__ import annotations

import os
from typing import Any

try:
    # Correct import path for newer Langfuse SDK versions
    from langfuse import Langfuse, observe
    
    # Initialize the Langfuse client if needed
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        print(f"INFO: Langfuse Client Initialized with Host: {os.getenv('LANGFUSE_HOST')}")
    else:
        print("WARNING: Langfuse Client: No API keys found.")

except Exception as e:
    print(f"ERROR: Langfuse SDK initialization error: {str(e)}")
    langfuse = None
    # Dummy observe if import fails
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
