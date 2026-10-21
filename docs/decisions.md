# Agronia — Architecture Decision Records

## 1. Purpose

This document records important technical decisions for Agronia.

Its purpose is to preserve the reasoning behind architectural choices, make trade-offs visible, and prevent AI coding agents from changing project direction without justification.

A decision recorded as planned is not necessarily implemented.

## 2. Decision Status

Use these statuses:

- **Proposed:** Under consideration.
- **Accepted:** Approved for the project.
- **Implemented:** Applied in the codebase and verified.
- **Superseded:** Replaced by a newer decision.
- **Rejected:** Evaluated and not selected.

Status changes should reflect actual project decisions and repository evidence.

## ADR-001: Project Scope

**Status:** Accepted as the current project direction.

### Context
Agronia is intended to address agricultural information needs throughout Timor-Leste.

### Decision
The overall project scope covers Timor-Leste rather than a single municipality.

### Consequences
- Research should consider the diversity of agricultural conditions across the country.
- The initial prototype may support fewer crops than the full project vision.
- Nationwide performance claims require appropriate evidence.

## ADR-002: Initial AI Use Case

**Status:** Accepted as the initial design direction.

### Context
A focused first use case is more feasible to evaluate than a large platform with many unrelated AI capabilities.

### Decision
Prioritize preliminary crop disease identification using computer vision.

### Consequences
- Dataset selection must determine the initial supported classes.
- Model outputs must communicate uncertainty.
- Additional AI capabilities should be considered separately.
- The model must not be presented as a replacement for agricultural specialists.

## ADR-003: Mobile Application Framework

**Status:** Accepted as the planned technology.

### Context
Agronia requires a mobile interface for farmers.

### Decision
Use Flutter and Dart for the intended mobile client.

### Consequences
- Frontend development will use Dart.
- API communication must follow documented contracts.
- Actual Flutter SDK and dependency compatibility must be verified.

This decision does not mean that the mobile application has already been implemented.

## ADR-004: Backend Framework

**Status:** Accepted as the planned technology.

### Context
The system needs an API, authentication, application logic, and database integration.

### Decision
Use Python and Django, with Django REST Framework for API development.

### Consequences
- Backend business logic should remain separate from mobile presentation.
- Request validation and permissions must be enforced on the server.
- Dependency versions must be confirmed before implementation.

## ADR-005: Initial Database

**Status:** Accepted for initial development.

### Context
The prototype needs persistent records without introducing unnecessary infrastructure.

### Decision
Use SQLite for early development.

PostgreSQL may be evaluated for production.

### Consequences
- Django migrations should manage schema changes.
- Production concurrency and operational requirements must be reviewed.
- A production database migration should be planned if justified.

## ADR-006: Existing Datasets Before Training From Scratch

**Status:** Accepted as the initial research strategy.

### Context
Training a reliable computer vision model from scratch can require substantial data, hardware, and experimentation.

### Decision
Investigate existing public datasets and pretrained models first.

### Consequences
- Dataset licensing must be checked.
- Model and dataset label compatibility must be verified.
- Transfer learning or fine-tuning may be considered.
- The final dataset and model remain unselected until research is completed.

## ADR-007: AI Inference Separation

**Status:** Accepted as the architectural direction.

### Context
Model implementations may change as the project evolves.

### Decision
Separate inference responsibilities from Django API presentation and business logic using a defined interface.

### Consequences
- The model can potentially be replaced without rewriting the entire backend.
- Preprocessing and class mapping require explicit contracts.
- A separate inference server is not required unless justified by measured needs.

## ADR-008: Preliminary Predictions and Uncertainty

**Status:** Accepted as a product and safety requirement.

### Context
A computer vision model may produce incorrect results, particularly for unsupported crops or unfamiliar images.

### Decision
Treat AI results as preliminary agricultural guidance, not definitive diagnoses.

### Consequences
- Unsupported inputs must be handled explicitly.
- Confidence values must not be treated as guarantees.
- Model limitations must be documented.
- Agricultural expert review should be encouraged when results are uncertain.

## ADR-009: API Versioning

**Status:** Accepted as the proposed API convention.

### Context
The mobile application and backend need a stable communication contract.

### Decision
Use `/api/v1/` as the planned REST API prefix.

### Consequences
- Endpoint contracts should be documented.
- Breaking API changes require deliberate versioning decisions.
- Actual routes must be verified against the implementation.

## ADR-010: Security and Privacy

**Status:** Accepted as a design requirement.

### Context
Agronia may process user accounts, uploaded photographs, and analysis history.

### Decision
Apply server-side authorization, input validation, controlled file storage, and secret management.

### Consequences
- Users must not access private records belonging to others.
- Uploaded files must be validated.
- Secrets must not be committed to Git.
- Privacy and retention requirements must be defined before field data collection.

## ADR-011: Offline Capabilities

**Status:** Proposed for future evaluation.

### Context
Internet access may be unreliable in some intended farming environments.

### Decision
Consider offline educational resources as a future capability. Evaluate offline AI inference separately.

### Consequences
- The initial design assumes online communication for remote inference.
- Offline functionality must not be advertised until implemented and tested.
- Local inference would require a compatible model runtime, device resources, and additional validation.

## ADR-012: Localization

**Status:** Proposed future capability.

### Context
Agronia serves a multilingual population.

### Decision
Plan for potential support of Tetum, Portuguese, and Indonesian.

### Consequences
- User-facing text should be localization-friendly.
- Agricultural terminology requires appropriate review.
- Language support should be claimed only when translations are implemented and tested.

## ADR-013: Model Evaluation Before Performance Claims

**Status:** Accepted as an evaluation requirement.

### Context
Benchmark performance may not reflect real-world conditions in Timor-Leste.

### Decision
Document model performance using held-out evaluation data and pursue local validation before making local effectiveness claims.

### Consequences
- Report per-class metrics where appropriate.
- Avoid data leakage between evaluation splits.
- Document dataset limitations.
- Do not invent accuracy figures or field outcomes.

## 3. Future Decision Template

Use the following structure when a new significant technical decision is made.

### ADR-XXX: Decision Title

**Status:** Proposed

**Date:** YYYY-MM-DD

**Context:** Explain the problem and constraints.

**Options considered:**
- Option A.
- Option B.
- Option C, if applicable.

**Decision:** State the selected option.

**Reasoning:** Explain why it was selected.

**Consequences:** Record benefits, trade-offs, and implementation implications.

**Verification:** Describe the evidence needed to confirm successful implementation.

## 4. Decision Management Rules

- Do not silently change an accepted decision.
- Record significant changes in a new decision entry.
- Explain why a previous choice no longer fits.
- Distinguish technical preferences from measured evidence.
- Update the status only after confirming the actual state.
- Keep decisions consistent with `design.md`, `architecture.md`, and `agents.md`.

## 5. Current Summary

Agronia's current design direction is a Flutter mobile client, Django REST API, SQLite for early development, and a computer vision component selected through dataset and model evaluation.

The exact dataset, model architecture, authentication mechanism, production database, hosting provider, and offline implementation remain to be determined.
