from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Xóa context cũ để tránh rò rỉ giữa các request
        clear_contextvars()

        # Lấy ID từ header hoặc tạo mới theo định dạng req-<8-char-hex>
        correlation_id = request.headers.get("x-request-id") or f"req-{uuid.uuid4().hex[:8]}"
        
        # Gắn ID vào structlog để mọi log sau này đều mang ID này
        bind_contextvars(correlation_id=correlation_id)
        
        request.state.correlation_id = correlation_id
        
        start = time.perf_counter()
        response = await call_next(request)
        
        # Gắn ID và thời gian xử lý vào Response Header
        duration = (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{duration:.2f}"
        
        return response
