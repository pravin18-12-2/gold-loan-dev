from fastapi import Header, HTTPException


def auth_headers(authorization: str = Header(...), x_tenant_id: str = Header(...)) -> dict:
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Invalid Authorization header')
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail='X-Tenant-ID is required')
    return {'tenant_id': x_tenant_id, 'token': authorization.split(' ', 1)[1]}
