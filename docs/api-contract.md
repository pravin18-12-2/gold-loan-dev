# Gold Loan API Contract (v1)

## Global rules
- Base URL: `https://api.yourdomain.com/api/v1`
- Required headers for authenticated endpoints:
  - `Authorization: Bearer <JWT>`
  - `X-Tenant-ID: <tenant_id>` (mandatory on all secured APIs)
  - `Content-Type: application/json`
- Critical POST endpoints must include `Idempotency-Key: <uuid>`.

## Standard response envelopes

### Success
```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-02-11T12:30:00Z",
    "version": "v1"
  }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Customer ID is required"
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-02-11T12:30:00Z",
    "version": "v1"
  }
}
```

## Immutable lifecycle rules
- Once `loan.status = COMPLETED`:
  - compliance API is forbidden (`403`)
  - purity API is forbidden (`403`)
  - update/patch operations are forbidden

## Idempotency behavior
For idempotent endpoints:
- Same `Idempotency-Key` + same request body returns original response.
- Duplicate resources must not be created.
- Persist records in `idempotency_record` (`key`, `endpoint`, `response_hash`, `created_at`).


## Compliance integrity
- `COUNT(jewel_images)` must equal `total_jewel_count`; mismatches are rejected.

## Append-only constraints
- `purity_test` and `loan_summary` are immutable (no updates/deletes).
