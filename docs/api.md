# Agronia — REST API Specification

## 1. Purpose

This document defines the API contract between the Agronia Flutter application and its Django backend.

Endpoint status is recorded per table. Endpoints marked **Implemented** have
been implemented and covered by automated tests in `backend/*/tests.py`.
Endpoints marked **Proposed** are still design intentions and must not be
assumed to exist.

## 2. API Principles

- Use a versioned API prefix: `/api/v1/`.
- Use JSON for ordinary request and response bodies.
- Use multipart form data for image uploads.
- Apply authentication and authorization where required.
- Validate all request data.
- Return consistent error structures.
- Do not expose internal exceptions.
- Document changes to the API contract.

## 3. Authentication

**Status: Implemented.** Token-based authentication using DRF's
`rest_framework.authtoken`.

Clients send the token on every protected request:

```text
Authorization: Token <token>
```

**Reasoning.** A mobile client talking to a JSON API integrates more simply
with a bearer token than with a session cookie, because a session cookie
requires the client to handle CSRF tokens and because browsers/clients can
leak cookies to unrelated hosts. Tokens are revocable individually, which
makes logout deterministic.

**Consequences.**

- Tokens are stored by the server and never expire automatically. Logout
  deletes the token, which revokes access immediately.
- The Flutter client must store the token in secure storage, not in plain
  preferences, once that feature is implemented.
- The token is the only credential sent. Passwords are never returned by any
  endpoint.
- `SessionAuthentication` remains enabled so the browsable API in Django
  admin can be used during development.

## 4. Endpoints

| Method | Endpoint | Purpose | Status |
|---|---|---|---|
| GET | `/api/v1/` | List available endpoints and API version | Implemented |
| POST | `/api/v1/auth/register/` | Register a user | Implemented |
| POST | `/api/v1/auth/login/` | Authenticate a user, returns a token | Implemented |
| POST | `/api/v1/auth/logout/` | Revoke the current token | Implemented |
| GET | `/api/v1/auth/me/` | Retrieve the current user's profile | Implemented |
| GET | `/api/v1/crops/` | List supported crops | Implemented |
| GET | `/api/v1/crops/{code}/` | Retrieve one crop | Implemented |
| GET | `/api/v1/diseases/` | List documented disease information | Implemented |
| GET | `/api/v1/diseases/{code}/` | Retrieve one disease record | Implemented |
| GET | `/api/v1/resources/` | List agricultural resources | Implemented |
| POST | `/api/v1/analyses/` | Submit an image for analysis | Implemented |
| GET | `/api/v1/analyses/` | List the current user's analysis history | Implemented |
| GET | `/api/v1/analyses/{id}/` | Retrieve an authorized analysis | Implemented |
| GET | `/api/v1/analyses/{id}/image/` | Retrieve the uploaded image, owner only | Implemented |

## 5. Image Analysis Request

**Endpoint:** `POST /api/v1/analyses/`

**Content type:** `multipart/form-data`

**Authentication:** required.

Fields:

| Field | Type | Required |
|---|---|---|
| `image` | Image file | Yes |
| `crop` | Supported crop identifier (slug, for example `padi`) | No |

`crop` is optional while the set of crops that the model can handle is still
being decided through dataset research. When supplied, it must reference an
active crop; unknown values are rejected.

The server validates the uploaded image by inspecting the file content, not
the filename extension or the client-supplied MIME type. The following rules
are enforced (configurable via `DJANGO_MAX_UPLOAD_SIZE_MB`):

- Maximum file size.
- Accepted formats: JPEG, PNG, WEBP.
- Minimum dimension of 64 pixels per side.
- Maximum of 40 million pixels, to limit decompression bomb impact.

The MVP model (`rice-mobilenetv2-v1`) supports four rice classes. Each
`class_id` must match an active `Disease.code`; run
`python manage.py seed_rice` after migrations to register `padi`, then
`padi-bacterial-blight`, `padi-sehat`, `padi-blast`, and `padi-tungro`.

## 6. Analysis Response

**Status: Implemented.** The following is an actual response shape produced
by the backend with the MVP rice model.

```json
{
  "id": "14da09ba-9184-4258-98ce-fed1c49ee500",
  "status": "completed",
  "crop": "padi",
  "predicted_disease": "padi-blast",
  "confidence": 0.8712,
  "model_version": "rice-mobilenetv2-v1",
  "message": "Prediksi: Blas (Blast).",
  "image_url": "/api/v1/analyses/14da09ba-9184-4258-98ce-fed1c49ee500/image/",
  "prediction": {
    "class_id": "padi-blast",
    "label": "Rice Blast",
    "confidence": 0.8712,
    "model_version": "rice-mobilenetv2-v1",
    "is_confident": true
  },
  "created_at": "2026-10-22T09:13:41.626849+08:00"
}
```

Class identifiers and labels are defined in `ai/classes.json`. A prediction
is only stored as `completed` when the returned `class_id` matches an active
`Disease` record. The model is not yet validated on local field images.

`confidence` is only populated when the inference implementation actually
produces a score. The API never fabricates confidence values.

`is_confident` compares the confidence against `AI_CONFIDENCE_THRESHOLD`
(default `0.60`). When it is `false`, the Flutter client shows an additional
uncertainty warning; the backend still returns the prediction rather than
inventing a diagnosis.

## 7. Analysis Status

**Status: Implemented.** Analysis is processed synchronously inside the
request. The `status` field is one of:

- `pending` — record created, inference not started.
- `processing` — inference running.
- `completed` — inference finished, a result is available.
- `failed` — inference could not complete. The `message` explains why.

Do not introduce asynchronous status handling unless the backend actually
supports it.

## 8. Error Format

**Status: Implemented.** Every error response, including Django-level 404
and 500 responses on `/api/` paths, uses this structure.

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Data yang dikirim tidak valid.",
    "details": {
      "image": ["Unggah gambar yang valid."]
    }
  }
}
```

`details` is only present when there are field-level problems.

Error codes in use:

| Code | HTTP status | Meaning |
|---|---|---|
| `invalid_request` | 400 | Request body or field validation failed |
| `invalid_credentials` | 401 | Username or password is wrong |
| `authentication_required` | 401 | Authentication is missing or invalid |
| `permission_denied` | 403 | Authenticated but not allowed |
| `not_found` | 404 | Resource does not exist or is not owned by the caller |
| `method_not_allowed` | 405 | Method not supported by the endpoint |
| `file_too_large` | 413 | Upload exceeds the configured limit |
| `unsupported_media_type` | 415 | Unsupported media type |
| `rate_limit_exceeded` | 429 | Rate limit exceeded |
| `internal_server_error` | 500 | Unexpected server failure |
| `inference_failed` | 502 | The AI service returned an invalid or unusable response |
| `model_unavailable` | 503 | The AI model is missing or is not loaded |
| `service_unavailable` | 503 | The AI service cannot be reached or did not respond |
| `unsupported_image` | 400 | The file is not a usable image |
| `unsupported_crop` | 400 | The requested crop is not supported |
| `unsupported_class` | 400 | The model produced a class that is not registered |

Messages are written for end users, not developers. Stack traces, internal
paths, and configuration values are never included.

## 9. HTTP Status Codes

Use status codes according to the actual failure or success condition.

| Status | Intended use |
|---|---|
| 200 | Successful retrieval or processing |
| 201 | Resource created |
| 400 | Invalid input |
| 401 | Authentication required or invalid |
| 403 | Permission denied |
| 404 | Resource not found |
| 413 | Request or upload exceeds allowed size |
| 415 | Unsupported media type |
| 429 | Rate limit exceeded, if configured |
| 500 | Unexpected server failure |
| 503 | Service unavailable |

## 10. Analysis History and Permissions

**Status: Implemented.** Analysis history is restricted to the authenticated
user who owns the records. Object-level ownership is enforced at the query
level (`Analysis.objects.filter(user=request.user)`) and at the detail
view.

The API does not allow users to retrieve another user's private images or
analysis records by changing an identifier. Attempts return `404` to avoid
leaking the existence of records that belong to other users.

Uploaded images are served through a dedicated endpoint that also checks
ownership and enforces `private, no-store` caching headers. Static media
serving is **disabled** for privacy reasons.

Administrative access must be explicitly defined and tested.

## 11. Validation Requirements

**Status: Implemented.**

Validate:
- Authentication and permissions.
- Required fields.
- Image format and actual file contents.
- File size.
- Supported crop identifiers.
- Requested record identifiers.
- Query parameters.
- Any user-provided text.

Do not rely solely on a client-provided MIME type or filename extension.
Image validation inspects the actual file contents with Pillow.

## 12. API Documentation and Testing

**Status: Implemented.**

- Request and response schemas are documented and tested.
- Authentication requirements are documented and tested.
- Expected errors are documented and tested.
- Valid requests tested.
- Malformed requests tested.
- Permission boundaries tested (unauthenticated, cross-user access).
- Image format/content validation tested.
- Behaviour when the AI model is unavailable tested (returns `503`,
  `status: "failed"`, no fake prediction).
- Error handler returns consistent JSON format.
- Tests run with `python manage.py test` from `backend/`.

## 13. Current Status

**Backend API foundation is implemented and tested.** Endpoints are
implemented under `/api/v1/` with token authentication, consistent error
formatting, strict image validation, owner-only access to history and private
images, and an AI inference interface that fails honestly on service or
model errors.

The Flutter client is integrated for login/register, image upload, result
rendering, and history using the contract above. The client never renders a
failed record as a diagnosis.

The inference component runs as a separate FastAPI service in `ai/`
(ADR-017). Django calls it over HTTP using `AI_SERVICE_URL`. The MVP model
`rice-mobilenetv2-v1` is loaded from `AI_MODEL_PATH`; matching crop and
disease records are created with `python manage.py seed_rice`. A live upload
then returns `completed` with a real prediction (verified through the API).

The service still returns `503 model_unavailable` when the model is not
configured, and `502 inference_failed` for invalid or unregistered
predictions. Failed attempts are recorded with `status: "failed"` and never
converted into a diagnosis. Field validation in Timor-Leste and the full
Flutter flow on a physical device remain pending.
