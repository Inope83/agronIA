# Agronia — Security and Privacy Requirements

## 1. Purpose

This document defines security and privacy requirements for Agronia.

The requirements apply to the Flutter client, Django backend, AI inference component, database, uploaded images, and deployment environment.

This is a security plan, not a security audit or a claim that the application is already secure.

## 2. Security Objectives

Agronia should:
- Protect user accounts and application data.
- Restrict access to private analysis records.
- Validate all untrusted inputs.
- Protect credentials and deployment secrets.
- Handle uploaded images safely.
- Minimize unnecessary personal data collection.
- Avoid exposing internal errors and sensitive logs.

## 3. Authentication

The backend must use an explicit authentication mechanism for protected resources.

Requirements:
- Verify authentication on protected endpoints.
- Use secure password handling provided by established framework mechanisms.
- Avoid storing plaintext passwords.
- Define session or token expiration behavior.
- Provide a suitable logout or revocation mechanism for the selected authentication design.
- Protect credentials during transport.

The authentication library and exact configuration remain to be selected.

## 4. Authorization

Authentication alone is not sufficient.

The backend must verify whether a user is allowed to access each requested resource.

Examples:
- A user should only see their own private analysis records.
- Administrative functions should require appropriate permissions.
- Uploaded images must not become public by default.
- User-controlled identifiers must not bypass ownership checks.

Authorization must be enforced on the server, not only by hiding frontend controls.

## 5. Secret Management

- Store secrets in environment variables or an appropriate secret-management system.
- Keep production secrets out of Git.
- Provide an example environment file containing placeholders only.
- Rotate any secret that has been accidentally exposed.
- Avoid printing credentials in logs.
- Separate development and production configuration.

Never place production passwords, private API keys, signing secrets, or database credentials in source code.

## 6. File Upload Security

Uploaded images are untrusted input.

Required controls:
- Enforce a configurable maximum file size.
- Validate the actual image format and readability.
- Use an image-processing library to decode images safely.
- Restrict accepted formats.
- Generate controlled storage names instead of trusting client filenames.
- Prevent path traversal.
- Handle corrupted and malformed files.
- Consider decompression bombs and excessive image dimensions.
- Keep private media access-controlled.
- Apply retention and deletion policies.

Do not assume that a `.jpg` filename guarantees that the file is a valid JPEG.

## 7. AI Inference Security

- Validate images before inference.
- Limit resource consumption.
- Handle model exceptions without exposing internal details.
- Avoid executing uploaded content as code.
- Do not load arbitrary model files supplied by users.
- Keep trusted model artifacts separate from user uploads.
- Record model versions used for analysis when feasible.

If third-party pretrained weights are used, verify their source and licensing before loading them.

## 8. Database Security

- Use Django ORM or parameterized database operations.
- Avoid unsafe construction of database queries.
- Apply permissions to data retrieval and modification.
- Protect production database credentials.
- Keep dependencies updated.
- Back up important data according to an established retention policy.
- Test restoration procedures before relying on backups.

SQLite is planned for initial development. Production database requirements should be assessed before deployment.

## 9. API Security

- Use HTTPS in production.
- Validate request bodies and query parameters.
- Configure allowed hosts and deployment settings correctly.
- Configure cross-origin policies only as required by the architecture.
- Apply appropriate rate limits where needed.
- Return controlled error messages.
- Avoid exposing stack traces in production.
- Protect sensitive endpoints against unauthorized access.
- Review authentication, authorization, and file-upload behavior through tests.

CORS is not a substitute for authentication or authorization.

## 10. Flutter Client Security

- Do not embed backend secrets in the mobile application.
- Store authentication credentials using suitable secure storage when required.
- Avoid logging tokens or private information.
- Validate user input before submission.
- Treat API responses as untrusted data.
- Avoid exposing private images in public application locations without a justified requirement.

Client-side validation improves usability but does not replace server-side validation.

## 11. Privacy and Data Minimization

Collect only information necessary for the intended features.

Before collecting user or field data:
- Define the purpose.
- Determine who can access it.
- Establish retention and deletion behavior.
- Provide appropriate information to users.
- Obtain consent where required.
- Avoid collecting unnecessary identifying information.

If local field images are collected, consider whether photographs contain identifiable people, private property, or location metadata.

Remove unnecessary image metadata where appropriate.

## 12. Logging and Monitoring

Logs may include:
- Request timestamps.
- Endpoint and status information.
- Error categories.
- Performance measurements.
- Non-sensitive diagnostic identifiers.

Do not log:
- Passwords.
- Authentication tokens.
- Private API keys.
- Unnecessary personal information.
- Full private image content.

Protect logs against unauthorized access and define retention periods appropriate to their purpose.

## 13. Dependency and Supply Chain Security

- Inspect dependency compatibility before upgrades.
- Prefer trusted package sources.
- Review the licenses of model weights and datasets.
- Monitor security advisories for important dependencies.
- Avoid adding unnecessary packages.
- Document significant dependency changes.

## 14. Deployment Security Checklist

Before production deployment, verify:
- Debug mode is disabled.
- Secret configuration is correct.
- HTTPS is enabled.
- Allowed hosts are configured.
- Authentication and permissions are tested.
- Uploaded media is protected.
- Database access is restricted.
- Backups and restoration are tested.
- Logs do not expose secrets.
- Dependencies are reviewed.
- Error responses do not reveal internal implementation details.

## 15. Incident Response

If a security issue is discovered:

1. Record the issue without exposing sensitive data.
2. Determine the affected component.
3. Limit further exposure.
4. Rotate compromised credentials when necessary.
5. Assess affected data and services.
6. Apply and test a fix.
7. Restore service safely.
8. Document the incident and prevention measures.

Follow applicable legal and organizational requirements when handling a real incident.

## 16. Current Status

These requirements must be implemented and verified during development. Their presence in this document does not establish that a security review has been completed.
