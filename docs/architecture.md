# Agronia — System Architecture

## 1. Document Purpose

This document defines the proposed technical architecture for Agronia.

The architecture is a design target, not a description of verified implementation. Actual repository contents and technology versions must be checked before development decisions are applied.

## 2. Architecture Overview

Agronia is planned as a client-server application with a separate AI inference responsibility.

### Components

1. **Flutter client**
   - User interface.
   - User input and image selection.
   - API communication.
   - Result presentation.
   - Authentication interface.

2. **Django backend**
   - Authentication and authorization.
   - Input validation.
   - Business logic.
   - Agricultural content management.
   - Analysis records.
   - API responses.

3. **AI inference component**
   - Image preprocessing.
   - Model inference.
   - Class-label mapping.
   - Prediction formatting.
   - Uncertainty handling.

4. **Database and file storage**
   - User and application records.
   - Agricultural content.
   - Analysis metadata.
   - Uploaded images where retention is necessary and authorized.

## 3. Logical Architecture

```text
Flutter Mobile Application
           |
           | HTTPS / JSON / Image Upload
           v
       Django REST API
           |
           +------ Authentication and Permissions
           |
           +------ Agricultural Content Services
           |
           +------ Analysis Management
           |
           | HTTP (AI_SERVICE_URL)
           v
     FastAPI AI Service (ai/)
           |
           v
     Computer Vision Model

Django Backend
      |
      +------ Database
      |
      +------ Controlled Image Storage
```

The diagram describes intended relationships. The backend/AI split is
implemented as described in ADR-017; the model itself is not yet available.

## 4. Flutter Client

### Responsibilities
- Display the application screens.
- Validate basic form input.
- Allow users to select or capture images.
- Communicate with the backend.
- Present prediction results and limitations.
- Display loading, empty, and error states.
- Manage authentication state securely.

### Design rules
- Separate UI widgets from network logic.
- Use typed models for API responses.
- Avoid hardcoding environment-specific URLs.
- Keep user-facing text ready for localization.
- Do not embed model credentials or server secrets.

## 5. Django Backend

### Responsibilities
- Expose versioned REST endpoints.
- Authenticate users where required.
- Validate uploaded files.
- Enforce object-level permissions.
- Coordinate inference requests.
- Store analysis metadata.
- Manage agricultural content.
- Return consistent responses.

### Suggested logical Django applications

These are proposed module boundaries, not confirmed existing folders.

- `accounts`: users, profiles, and authentication.
- `agriculture`: crop, disease, and educational content.
- `analysis`: image submissions and prediction records.
- `common`: shared utilities and error-handling conventions.

The inference component is not a Django app. It runs as a separate FastAPI
project in `ai/` and is reached over HTTP (ADR-017).

Create only the modules needed by the agreed implementation scope.

## 6. AI Inference Component

The inference component should expose a stable internal interface.

### Responsibilities
- Load the configured model.
- Validate expected input dimensions and format.
- Preprocess images consistently with training.
- Run inference.
- Map output indices to documented labels.
- Return structured results.
- Handle unsupported inputs and inference failures.

### Design requirements
- Avoid duplicating model-loading logic across API views.
- Record the model version where feasible.
- Keep inference errors distinct from valid predictions.
- Provide a clear mechanism for replacing the model.
- Do not interpret model confidence as a guarantee of correctness.

Inference runs as a separate FastAPI service (`ai/`) and is called over
HTTP by the `analysis` app. The Django project must not import model code,
weights, training dependencies, or dataset tooling. See ADR-017.

## 7. Database

### Initial development
SQLite is the planned initial database.

### Potential production database
PostgreSQL may be considered after evaluating hosting, concurrent access, operational requirements, and migration needs.

### Proposed data entities

- User.
- User profile, if required.
- Crop.
- Disease.
- Agricultural resource.
- Analysis record.
- Prediction result.
- Model version metadata.

These entities are conceptual. Exact models, relationships, and fields must be defined during implementation.

### Data management rules
- Use Django migrations.
- Keep relationships explicit.
- Avoid storing duplicate information unnecessarily.
- Restrict access to user-owned records.
- Define image retention and deletion behavior.

## 8. Image Storage

Image files should not be stored directly in database records unless a specific design requirement justifies doing so.

The database may store controlled file references and metadata.

Storage decisions should consider:
- Access permissions.
- Maximum upload size.
- File retention.
- Backup and recovery.
- Storage costs.
- Privacy requirements.

Private user images should not be served through unrestricted public URLs.

## 9. Prediction Data Flow

1. The user selects an image.
2. The client submits the image and any required crop information.
3. The API validates authentication, request data, and file constraints.
4. The analysis service invokes the inference interface.
5. The model processes the image.
6. The inference layer maps outputs to supported labels.
7. The backend constructs a response with prediction and limitation information.
8. The backend records the result where appropriate.
9. The client presents the response.

If inference fails, the API should return a controlled error rather than fabricate a result.

## 10. Error Handling

The system should distinguish:
- Invalid input.
- Unsupported image or crop class.
- Authentication failure.
- Permission denial.
- Model unavailability.
- Processing timeout.
- Unexpected server error.

Error responses must not expose stack traces, secrets, or internal server details.

## 11. Deployment Architecture

The deployment arrangement has not been selected.

A possible production setup includes:
- A hosted Django application.
- The separately deployed FastAPI inference service (`ai/`).
- A compatible Python inference runtime.
- A production database.
- Controlled media storage.
- HTTPS termination.
- Application logs and monitoring.

Model size, memory use, CPU/GPU requirements, and expected request volume must be measured before choosing hosting infrastructure.

## 12. Network and Offline Considerations

The initial architecture assumes online communication between Flutter and Django for remote inference.

Offline access to educational content may be explored separately.

Offline AI inference would require packaging a compatible model and preprocessing pipeline into an appropriate runtime or using a local inference service. It must not be treated as available until implemented and tested.

## 13. Architecture Evolution

The architecture should evolve through documented, incremental decisions.

A component may be separated into another service when there is evidence of a need, such as:
- Excessive inference latency.
- Independent scaling requirements.
- Resource isolation.
- Deployment constraints.

Avoid adding distributed infrastructure before the prototype demonstrates a practical need.
