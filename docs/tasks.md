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

- [ ] Review repository structure.
- [ ] Confirm the active Git branch and working tree.
- [ ] Review `README.md`.
- [ ] Review `design.md`.
- [ ] Review `agents.md`.
- [ ] Review `skill.md`.
- [ ] Review `context.md`.
- [ ] Review `architecture.md`.
- [ ] Review `roadmap.md`.
- [ ] Review `dataset.md`.
- [ ] Review `ai-model.md`.
- [ ] Review `api.md`.
- [ ] Review `security.md`.
- [ ] Review `decisions.md`.
- [ ] Resolve conflicting requirements.
- [ ] Define the first prototype scope.

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

- [ ] Confirm Python and Django compatibility.
- [ ] Establish backend application structure.
- [ ] Configure environment variables.
- [ ] Configure the development database.
- [ ] Define application data models.
- [ ] Implement authentication as required.
- [ ] Implement API input validation.
- [ ] Implement the agricultural content interface.
- [ ] Implement the analysis workflow.
- [ ] Integrate the inference interface.
- [ ] Implement consistent error responses.
- [ ] Add backend tests.
- [ ] Document API behavior.

**Completion criteria:** The backend passes relevant tests and can process valid requests according to the agreed API contract.

## 7. Phase 5 — Flutter Application

- [ ] Confirm Flutter and Dart compatibility.
- [ ] Establish the mobile application structure.
- [ ] Implement the initial navigation.
- [ ] Implement authentication screens.
- [ ] Implement image selection.
- [ ] Implement API communication.
- [ ] Implement loading and error states.
- [ ] Implement prediction result display.
- [ ] Implement analysis history if included in the initial scope.
- [ ] Test network failure handling.
- [ ] Test on an appropriate emulator or physical device.

**Completion criteria:** The mobile client can complete the agreed end-to-end workflow.

## 8. Phase 6 — Integration and Validation

- [ ] Verify the client and backend use the same API contract.
- [ ] Test valid image uploads.
- [ ] Test invalid and unsupported inputs.
- [ ] Test authentication and permissions.
- [ ] Test model failures and timeouts.
- [ ] Review image storage permissions.
- [ ] Validate user-facing explanations.
- [ ] Collect initial user feedback if available.
- [ ] Seek agricultural expert feedback where possible.
- [ ] Document unresolved issues.

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
