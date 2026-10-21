# Agronia — Development Roadmap

## 1. Purpose

This roadmap defines the proposed sequence for developing Agronia from a documented concept into a validated prototype.

The phases are dependency-based rather than tied to fixed calendar dates. Their duration will depend on dataset suitability, development capacity, model requirements, and access to agricultural feedback.

## 2. Phase Overview

| Phase | Focus | Expected result |
|---|---|---|
| 1 | Project foundation | Consistent documentation and scope |
| 2 | Dataset research | Documented dataset selection |
| 3 | AI baseline | Initial evaluation results |
| 4 | Backend | Tested Django API |
| 5 | Mobile client | Flutter workflow |
| 6 | Integration | End-to-end prototype |
| 7 | Validation | Technical and user feedback |
| 8 | Deployment | Reproducible hosted demonstration |

These are planned milestones, not completed achievements.

## 3. Phase 1 — Project Foundation

### Objectives
- Confirm the project structure.
- Review the core documentation.
- Define the initial supported use case.
- Confirm technology compatibility.
- Establish development conventions.

### Deliverables
- Reviewed project documentation.
- Defined initial scope.
- Updated task list.
- Recorded technical decisions.

### Exit criteria
The team can explain the first workflow, intended architecture, and unresolved requirements.

## 4. Phase 2 — Dataset Research

### Objectives
- Investigate public crop disease datasets.
- Verify source and license information.
- Compare supported crop and disease classes.
- Assess data quality and local relevance.
- Select a suitable baseline dataset.

### Deliverables
- Dataset comparison.
- Documented license review.
- Proposed class mapping.
- Data preparation and evaluation plan.

### Exit criteria
A candidate dataset has been selected with documented reasons and limitations.

## 5. Phase 3 — AI Baseline

### Objectives
- Identify a compatible pretrained model or baseline approach.
- Confirm preprocessing and class labels.
- Run reproducible evaluation.
- Measure relevant classification metrics.
- Identify failure cases.

### Deliverables
- Baseline evaluation report.
- Model limitations.
- Supported class list.
- Recommendation on whether fine-tuning is needed.

### Exit criteria
The project has evidence of baseline behavior on held-out data.

## 6. Phase 4 — Backend Development

### Objectives
- Establish Django and Django REST Framework.
- Define data models and API contracts.
- Implement validation and access controls.
- Add the inference integration interface.
- Create automated tests.

### Deliverables
- Backend implementation.
- API documentation.
- Test results.
- Development setup instructions.

### Exit criteria
The backend can validate requests and return structured results or controlled errors.

## 7. Phase 5 — Mobile Application

### Objectives
- Create the main Flutter screens.
- Implement image selection and upload.
- Connect to the Django API.
- Display predictions and limitations.
- Handle connectivity problems.

### Deliverables
- Mobile client prototype.
- API integration.
- Basic error and loading states.
- Device testing notes.

### Exit criteria
The client can complete the intended image submission and result-display workflow.

## 8. Phase 6 — End-to-End Integration

### Objectives
- Verify communication across all components.
- Test successful and failed inference requests.
- Confirm data persistence and permissions.
- Check user-facing result messages.
- Fix integration defects.

### Deliverables
- End-to-end test results.
- Defect list.
- Updated documentation.
- Demonstration workflow.

### Exit criteria
A repeatable demonstration works under documented conditions.

## 9. Phase 7 — Validation

### Objectives
- Evaluate the model beyond a training dataset.
- Seek feedback from farmers and agricultural specialists.
- Investigate local image conditions.
- Identify misunderstandings in the interface.
- Record limitations and improvements.

### Deliverables
- Validation plan and available results.
- User feedback summary.
- Model and usability improvement priorities.

### Exit criteria
The team can describe what the prototype has demonstrated and what remains unverified.

Field testing must follow appropriate consent, privacy, and data-handling practices.

## 10. Phase 8 — Deployment

### Objectives
- Select hosting compatible with the model.
- Configure production security.
- Prepare database and file storage.
- Verify deployment and recovery procedures.
- Document operational requirements.

### Deliverables
- Deployment configuration.
- Installation and maintenance instructions.
- Basic monitoring and backup procedures.
- Demonstration URL, if a deployment is completed.

### Exit criteria
The application is accessible in the intended environment and critical workflows have been tested.

## 11. Future Roadmap

Potential later developments include:
- Expanded crop and disease coverage.
- Tetum, Portuguese, and Indonesian interfaces.
- Offline agricultural educational resources.
- Local expert review workflows.
- Weather and seasonal farming information.
- Additional computer vision tasks.
- Carefully evaluated offline inference.

Each feature requires a separate scope, feasibility assessment, and validation plan.

## 12. Roadmap Management

Update this roadmap when:
- Dataset limitations change the initial crop scope.
- Model requirements affect the infrastructure.
- Field feedback changes user priorities.
- Security or reliability requirements introduce new work.
- A phase has been completed and verified.

Prefer a smaller validated prototype over a broad collection of untested features.
