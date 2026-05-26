"""Small JSON-RPC response helpers shared by A2A HTTP surfaces."""

from __future__ import annotations

from typing import Any

from a2a.types import (
    JSONRPCError,
    JSONRPCErrorResponse,
    JSONRPCRequest,
    JSONRPCSuccessResponse,
)


def jsonrpc_success(request: JSONRPCRequest, result: Any) -> dict[str, Any]:
    return JSONRPCSuccessResponse(
        id=request.id,
        result=result,
    ).model_dump(mode="json", exclude_none=True)


def jsonrpc_error(
    request_id: str | int | None,
    *,
    code: int,
    message: str,
    data: Any | None = None,
) -> dict[str, Any]:
    return JSONRPCErrorResponse(
        id=request_id,
        error=JSONRPCError(code=code, message=message, data=data),
    ).model_dump(mode="json", exclude_none=True)
