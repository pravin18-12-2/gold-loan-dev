import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def meta():
    return {
        'request_id': str(uuid.uuid4()),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': 'v1',
    }


def success(data):
    return {'success': True, 'data': data, 'meta': meta()}


async def http_exception_handler(_: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        status = exc.status_code
        message = str(exc.detail)
    else:
        status = 500
        message = 'Internal server error'
    return JSONResponse(
        status_code=status,
        content={
            'success': False,
            'error': {'code': 'HTTP_ERROR', 'message': message},
            'meta': meta(),
        },
    )
