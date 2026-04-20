from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Dọn dẹp ngữ cảnh
        clear_contextvars()

        # Tạo định danh cho mỗi request
        header_request_id = request.headers.get("x-request-id")
        if header_request_id:
            correlation_id = header_request_id
        else:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"
        
        # Nhúng mã định danh vào ngữ cảnh 
        bind_contextvars(correlation_id=correlation_id)

        # Lưu mã định danh vào vào đối tượng request
        request.state.correlation_id = correlation_id
        
        # Tính khoảng thời gian thực thi của mdw
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        # Gắn ID định danh ở trên vào header và trả về cho người dùng
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(duration * 1000)
        return response