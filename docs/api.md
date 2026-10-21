# Agronia — REST API Specification

## 1. Purpose

This document defines the proposed API contract between the Agronia Flutter application and its Django backend.

All endpoints in this document are proposed. They must not be treated as implemented or available until confirmed in the source code.

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

The authentication mechanism has not yet been selected.

Possible approaches include Django REST Framework authentication options or token-based authentication.

The final choice must consider Flutter integration, token storage, session lifecycle, and deployment requirements.

## 4. Proposed Endpoints

| Method | Proposed endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register/` | Register a user |
| POST | `/api/v1/auth/login/` | Authenticate a user |
| POST | `/api/v1/auth/logout/` | End the supported authentication session |
| GET | `/api/v1/auth/me/` | Retrieve the current user's profile |
| GET | `/api/v1/crops/` | List supported crops |
| GET | `/api/v1/diseases/` | List documented disease information |
| POST | `/api/v1/analyses/` | Submit an image for analysis |
| GET | `/api/v1/analyses/` | List the current user's analysis history |
| GET | `/api/v1/analyses/{id}/` | Retrieve an authorized analysis |
| GET | `/api/v1/resources/` | List agricultural resources |

These endpoint names are a starting proposal. Registration, logout, and authentication routes depend on the selected authentication implementation.

## 5. Image Analysis Request

**Proposed endpoint:** `POST /api/v1/analyses/`

**Content type:** `multipart/form-data`

Proposed fields:

| Field | Type | Required |
|---|---|---|
| `image` | Image file | Yes |
| `crop_type` | Supported crop identifier | To be decided |

The server must validate the uploaded image, enforce configured size limits, and reject invalid or unsupported inputs.

## 6. Illustrative Success Response

The following JSON is an example of a proposed response contract, not an actual model result.

```json
{
  "id": "example-analysis-id",
  "status": "completed",
  "prediction": {
    "class_id": "example-class",
    "label": "Example disease label",
    "confidence": null
  },
  "model_version": "example-version",
  "message": "This result is preliminary and may require expert review."
}
```

The example identifiers and labels are placeholders. The actual response schema must be finalized after selecting the model and database design.

The `confidence` field should only contain a meaningful value when the selected inference implementation provides one. The API must not fabricate scores.

## 7. Analysis Status

A synchronous implementation may return a completed result directly.

If processing is later implemented asynchronously, the API may use explicit states such as:
- `pending`
- `processing`
- `completed`
- `failed`

Do not introduce asynchronous status handling unless the backend actually supports it.

## 8. Proposed Error Format

```json
{
  "error": {
    "code": "invalid_image",
    "message": "The submitted image could not be processed."
  }
}
```

This is an illustrative structure. The actual error format should be consistent across endpoints.

Potential error categories:
- Invalid request.
- Unsupported file.
- File too large.
- Authentication required.
- Permission denied.
- Resource not found.
- Model unavailable.
- Processing timeout.
- Internal server error.

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

The exact codes depend on endpoint semantics and the configured framework behavior.

## 10. Analysis History and Permissions

Analysis history should be restricted to the authenticated user who owns the records, unless a specific authorized administrative workflow applies.

Administrative access must be explicitly defined and tested.

The API must not allow users to retrieve another user's private images or analysis records by changing an identifier.

## 11. Validation Requirements

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

## 12. API Documentation and Testing

Before implementation is considered complete:
- Finalize request and response schemas.
- Document authentication requirements.
- Document expected errors.
- Test valid requests.
- Test malformed requests.
- Test permission boundaries.
- Verify consistency between Django and Flutter.
- Update this document when the contract changes.

## 13. Current Status

This file defines a proposed API contract. No endpoint should be assumed to exist until it is implemented and verified.
