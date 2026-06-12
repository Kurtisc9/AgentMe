from __future__ import annotations

import json
import traceback
from datetime import UTC, datetime
from pathlib import Path

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class StructuredExceptionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_path: str = "logs/errors.jsonl") -> None:
        super().__init__(app)
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            event = {
                "timestamp": datetime.now(UTC).isoformat(),
                "method": request.method,
                "path": request.url.path,
                "error_type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event) + "\n")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error."},
            )
