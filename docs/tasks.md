# Agronia — Development Tasks

## 1. Purpose

This document tracks planned development work for Agronia.

The initial status of tasks is set to `Not Started` because implementation progress has not been verified through repository inspection.

Update the status only when there is evidence that the work has been completed or started.

## 2. Status Definitions

- `Not Started`: Work has not begun.
- `In Progress`: Work is actively underway.
- `Blocked`: Work cannot proceed because of an unresolved dependency.
- `Done`: Work has been completed and checked.
- `Needs Review`: Work exists but requires further verification.

## 3. Phase 1 — Repository and Documentation

- [x] Review repository structure.
- [x] Confirm the active Git branch and working tree.
- [x] Review `README.md`.
- [x] Review `design.md`.
- [x] Review `agents.md`.
- [x] Review `skill.md`.
- [x] Review `context.md`.
- [x] Review `architecture.md`.
- [x] Review `roadmap.md`.
- [x] Review `dataset.md`.
- [x] Review `ai-model.md`.
- [x] Review `api.md`.
- [x] Review `security.md`.
- [x] Review `decisions.md`.
- [x] Review `ui-ux.md`.
- [x] Resolve conflicting requirements (documented in audit report).
- [x] Define the first prototype scope (documented).

**Update (2026-10-22):** Audit Phase 1 selesai. `docs/` di-pull dari `origin/main` (PR #4). Branch `backend-foundation` dibuat. File typo `MASTER_PPROMP.md` dihapus.

## 4. Phase 2 — Dataset Research

- [ ] Identify candidate crop disease datasets.
- [ ] Record dataset sources and licenses.
- [ ] Identify supported crops and disease classes.
- [ ] Compare image quality and class distribution.
- [ ] Evaluate relevance to Timor-Leste.
- [ ] Select a candidate dataset for baseline experiments.
- [ ] Document preprocessing requirements.
- [ ] Define training, validation, and test splits.
- [ ] Check for duplicate images and data leakage.

**Completion criteria:** A documented dataset selection supported by source, licensing, class, and quality information.

## 5. Phase 3 — AI Baseline

- [ ] Identify candidate pretrained models.
- [ ] Verify model licensing and dependencies.
- [ ] Confirm model input and output formats.
- [ ] Establish a reproducible evaluation procedure.
- [ ] Evaluate the baseline on held-out data.
- [ ] Calculate relevant classification metrics.
- [ ] Review per-class performance.
- [ ] Identify unsupported inputs and failure cases.
- [ ] Document model limitations.
- [ ] Decide whether fine-tuning is justified.

**Completion criteria:** A reproducible baseline evaluation with documented limitations.

## 4. Phase 2 — Dataset Research

- [ ] Identify candidate crop disease datasets.
- [ ] Record dataset sources and licenses.
- [ ] Identify supported crops and disease classes.
- [ ] Compare image quality and class distribution.
- [ ] Evaluate relevance to Timor-Leste.
- [ ] Select a candidate dataset for baseline experiments.
- [ ] Document preprocessing requirements.
- [ ] Define training, validation, and test splits.
- [ ] Check for duplicate images and data leakage.

**Completion criteria:** A documented dataset selection supported by source, licensing, class, and quality information.

## 5. Phase 3 — AI Baseline

- [ ] Identify candidate pretrained models.
- [ ] Verify model licensing and dependencies.
- [ ] Confirm model input and output formats.
- [ ] Establish a reproducible evaluation procedure.
- [ ] Evaluate the baseline on held-out data.
- [ ] Calculate relevant classification metrics.
- [ ] Review per-class performance.
- [ ] Identify unsupported inputs and failure cases.
- [ ] Document model limitations.
- [ ] Decide whether fine-tuning is justified.

**Completion criteria:** A reproducible baseline evaluation with documented limitations.

## 6. Phase 4 — Django Backend

- [x] Confirm Python and Django compatibility. (Python 3.14.8, Django 5.2.18, DRF 3.18.3)
- [x] Establish backend application structure. (apps: `accounts`, `agriculture`, `analysis`, `common`; inference moved to `ai/`, ADR-017)
- [x] Configure environment variables. (`config/env.py`, `.env.example`, split settings base/dev/prod)
- [x] Configure the development database. (SQLite, migrations applied)
- [x] Define application data models. (`Crop`, `Disease`, `AgriculturalResource`, `Analysis`, `Profile`)
- [x] Implement authentication as required. (Token auth: register/login/logout/me)
- [x] Implement API input validation. (image content validation, crop lookup, auth)
- [x] Implement the agricultural content interface. (`/api/v1/crops/`, `/api/v1/diseases/`, `/api/v1/resources/`)
- [x] Implement the analysis workflow. (owner-only, private image access via `/api/v1/analyses/{id}/image/`, sync processing)
- [x] Integrate the inference interface. (FastAPI `ai/` service over HTTP; honest `model_unavailable`)
- [x] Implement consistent error responses. (global exception handler + JSON handlers for 404/500)
- [x] Add backend tests. (43 tests, all pass)
- [x] Document API behavior. (`docs/api.md` updated)

**Update (2026-10-22):** Backend foundation implemented on branch `backend-foundation`. No fake AI results; model unavailable returns `503` with `status: "failed"` and history recorded. Private images served via owner-only endpoint (static media serving disabled). Generated files (`db.sqlite3`, `__pycache__`) removed from tracking and added to `.gitignore`. `requirements.txt` added.

**Update (2026-10-22, ADR-017):** Backend and AI service are now separate
projects: `backend/` (Django) and `ai/` (FastAPI). The duplicate `ai_old/`
tree and circular `backend/media` symlink were removed. AI errors are mapped
to `service_unavailable`, `model_unavailable`, or `inference_failed`; the
backend tests mock the AI service instead of depending on a local process.

**Completion criteria:** The backend passes relevant tests and can process valid requests according to the agreed API contract.

## 7. Phase 5 — Flutter Application

- [x] Confirm Flutter and Dart compatibility. (Flutter 3.44.0, Dart 3.12.0)
- [x] Establish the mobile application structure. (`lib/core`, `lib/shared`, `lib/features`)
- [x] Implement the initial navigation. (Home, Analyze, History, Learn via bottom navigation)
- [ ] Implement authentication screens.
- [x] Implement image selection. (gallery; camera on Android/iOS, client-side type and 10 MB size checks)
- [ ] Implement API communication.
- [x] Implement loading and error states. (reusable widgets; not yet connected to network flows)
- [x] Implement prediction result display. (layout only; not reachable until API integration)
- [ ] Implement analysis history if included in the initial scope.
- [ ] Test network failure handling.
- [ ] Test on an appropriate emulator or physical device.

**Update (2026-10-22):** Flutter UI foundation implemented. Theme follows `docs/ui-ux.md` tokens; empty states are honest (no invented results or statistics). Analyze submission explicitly reports that image upload and AI analysis are not connected yet. `flutter analyze` reports no issues, 3 widget tests pass, Linux debug build succeeds.

**Update (2026-10-22, Phase 6):** Client integration implemented against
`docs/api.md`: token login/register, authenticated image upload, analysis
result rendering, and owner-scoped history. Tokens are stored with
`flutter_secure_storage`. API base URL defaults to `http://127.0.0.1:8000/api/v1`
and can be overridden with `--dart-define=API_BASE_URL=...`. Failures are
never converted into a diagnosis: `service_unavailable`, `model_unavailable`,
`inference_failed`, validation errors, and network failures are shown as
failures. `flutter analyze` is clean; 12 tests pass; Linux debug build
succeeds.

**Update (2026-10-22, konektivitas):** Fixed `BASE_DIR` so `backend/.env`,
SQLite, and media resolve to `backend/` (previously `backend/config/`).
Development `ALLOWED_HOSTS` now merges `DJANGO_ALLOWED_HOSTS` instead of
replacing it. Android debug builds allow cleartext HTTP for local development;
the release manifest requests `INTERNET`. Verified over LAN: register,
`GET /crops/`, and upload returning `503 model_unavailable` via
`http://192.168.1.189:8000`. Physical devices still need
`--dart-define=API_BASE_URL=http://<IP-LAN>:8000/api/v1`.

**Completion criteria:** The mobile client can complete the agreed end-to-end workflow.

## 8. Phase 6 — Integration and Validation

- [x] Verify the client and backend use the same API contract. (client parses documented fields; contract tests added)
- [x] Test valid image uploads. (live backend upload verified; client multipart test; full success blocked by missing model)
- [x] Test invalid and unsupported inputs. (backend validation suite plus client-side type and size checks)
- [x] Test authentication and permissions. (backend auth suite; client login and error parsing)
- [x] Test model failures and timeouts. (unreachable service, `model_unavailable`, `inference_failed`, and timeout mapping)
- [x] Review image storage permissions. (owner-only image endpoint tests)
- [ ] Validate user-facing explanations.
- [ ] Collect initial user feedback if available.
- [ ] Seek agricultural expert feedback where possible.
- [x] Document unresolved issues. (missing model and pending physical-device test recorded here and in ADR-017)

**Completion criteria:** Integration tests pass and known limitations are documented.

## 9. Phase 7 — Deployment Preparation

- [ ] Select a suitable hosting environment.
- [ ] Estimate model memory and compute requirements.
- [ ] Configure production environment variables.
- [ ] Configure HTTPS.
- [ ] Configure database and media storage.
- [ ] Review production access controls.
- [ ] Configure logs and basic monitoring.
- [ ] Test database backup and recovery procedures.
- [ ] Prepare deployment instructions.
- [ ] Verify the deployed application.

**Completion criteria:** A reproducible deployment with tested critical workflows and documented recovery procedures.

## 10. Current Priority

The recommended next work is:

1. Verify the current repository and documentation.
2. Finalize the initial crop and disease scope.
3. Research suitable existing datasets.
4. Evaluate candidate pretrained models.
5. Begin implementation after the architecture and API contract are sufficiently defined.

Do not mark any task as done solely because a plan or document has been written.
