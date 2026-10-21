# Agronia — Development Skill Guide

## 1. Skill Overview

This document defines reusable development procedures for Agronia.

The skill covers:
- Repository inspection.
- Dataset evaluation.
- Computer vision model integration.
- Django API development.
- Flutter integration.
- Agricultural prediction quality.
- Testing and documentation.

The purpose is to help developers and AI coding agents follow a consistent workflow instead of improvising a different architecture for every task.

## 2. Skill Activation

Use the relevant procedure when a task involves:
- Starting or restructuring the project.
- Selecting an existing AI dataset.
- Evaluating a crop disease model.
- Adding a Django API endpoint.
- Integrating Flutter with Django.
- Troubleshooting model predictions.
- Testing or preparing deployment.

Read `design.md` for architectural decisions and `agents.md` for repository and coding rules.

## 3. Repository Inspection Procedure

Before making changes:

1. Identify the repository root.
2. Inspect the current folder structure.
3. Check `git status` and the current branch.
4. Read `README.md` and the project documentation.
5. Identify existing frontend, backend, and AI components.
6. Inspect dependency files and environment requirements.
7. Determine whether the requested feature already exists.

Output:
- A short summary of the existing structure.
- The relevant files.
- Missing requirements.
- The recommended next step.

Do not recreate existing components without a reason.

## 4. Dataset Discovery Procedure

### Step 1: Define the Initial Scope

Identify the crops and disease classes that the first prototype will support.

Do not assume that a model supports every crop grown in Timor-Leste.

### Step 2: Search Existing Datasets

Evaluate public datasets and existing pretrained models before collecting a new dataset.

Possible research sources include:
- PlantVillage datasets.
- Public crop disease datasets on Kaggle.
- Research datasets published by universities or agricultural institutions.
- Model and dataset repositories with documented licenses.

These are candidate sources, not confirmation that a specific dataset is suitable or legally reusable.

### Step 3: Evaluate Dataset Quality

For each candidate, record:
- Dataset name and source.
- License and usage restrictions.
- Supported crops.
- Disease and healthy-image classes.
- Number of images per class, when documented.
- Image conditions and quality.
- Known biases and limitations.
- Suitability for Timor-Leste.

### Step 4: Check Class Compatibility

Compare the dataset labels with the labels expected by the selected model.

Different datasets may use different class names or taxonomies. Do not merge incompatible labels without an explicit mapping and justification.

### Step 5: Prepare Evaluation Splits

Separate training, validation, and test data appropriately.

Prevent near-duplicate images or images from the same source from leaking across splits when this would inflate evaluation results.

### Expected Output

Produce a dataset comparison and a recommendation explaining why the chosen candidate fits the initial prototype.

Do not download or train on a dataset until its suitability and permitted use have been checked.

## 5. AI Model Evaluation Procedure

### Step 1: Establish a Baseline

Evaluate a suitable pretrained model or a model trained on an existing dataset.

Record the original model, supported classes, expected input format, and licensing conditions.

### Step 2: Verify Input Processing

Confirm:
- Required image dimensions.
- Color channel order.
- Pixel normalization.
- Supported file formats.
- Preprocessing consistency with the model.

Incorrect preprocessing can produce unreliable predictions.

### Step 3: Evaluate Performance

Use an appropriate held-out test set and report:
- Overall accuracy where meaningful.
- Per-class precision and recall.
- F1-score.
- Confusion matrix.
- Performance on underrepresented classes.
- Known failure cases.

Do not rely on accuracy alone when classes are imbalanced.

### Step 4: Evaluate Real-World Limitations

Check whether the model can handle:
- Different lighting conditions.
- Blurry images.
- Complex backgrounds.
- Multiple leaves or symptoms in one image.
- Unseen crops and diseases.
- Images that do not contain a crop.

Do not claim these cases are solved unless testing supports the claim.

### Step 5: Define Uncertainty Handling

If the system cannot produce a reliable result, return an appropriate uncertainty message instead of presenting a potentially misleading disease diagnosis.

A confidence threshold must be selected using validation data, not an arbitrary number presented as scientifically established.

### Expected Output

Document the model version, supported classes, evaluation results, limitations, and recommended next steps.

## 6. Django API Development Procedure

When adding a backend feature:

1. Identify the responsible Django application.
2. Define the request and response contract.
3. Validate the input data.
4. Implement business logic in an appropriate service or application layer.
5. Apply authentication and permissions.
6. Implement consistent error handling.
7. Add tests.
8. Update API documentation.

For crop image analysis, the endpoint should validate the image before passing it to the inference component.

Do not place the entire model-loading and inference implementation directly inside a large API view.

### Expected Output

- Implemented endpoint or service.
- Documented request and response formats.
- Tests covering valid and invalid requests.
- Security and permission considerations.

## 7. AI Inference Integration Procedure

The inference component should provide a stable interface between Django and the selected model.

Responsibilities:
- Load the model using a controlled initialization process.
- Preprocess valid images.
- Run inference.
- Map model outputs to documented class labels.
- Return structured results.
- Handle invalid inputs and model errors.
- Expose model metadata when appropriate.

Do not reload large model files for every request unless the deployment architecture specifically requires it.

The inference layer should not be responsible for managing user accounts or frontend presentation.

## 8. Flutter Integration Procedure

When connecting the mobile application to Django:

1. Confirm the API base URL for the current environment.
2. Define request and response models.
3. Implement the API client.
4. Add authentication handling when required.
5. Validate image selection.
6. Upload the image using the agreed API format.
7. Display loading, success, empty, and error states.
8. Handle timeouts and unavailable servers.
9. Test the complete request flow.

A development server running on a computer may not be accessible through `localhost` on a physical phone. Configure the correct network address or emulator-specific address.

Do not hardcode a production server address into application logic.

## 9. Agricultural Recommendation Procedure

Recommendations must be grounded in reliable agricultural references.

For each disease:
- Record the disease name and affected crop.
- Describe recognizable symptoms.
- Explain prevention and management options.
- Identify the source of the information.
- Distinguish general advice from locally validated guidance.
- Avoid unsupported chemical treatment instructions.

When the model's result is uncertain, recommend further inspection or consultation with an agricultural specialist.

Do not present a computer vision prediction as definitive proof of a disease.

## 10. Localization Procedure

Agronia targets farmers throughout Timor-Leste.

Plan for future support of:
- Tetum.
- Portuguese.
- Indonesian.

Use a localization-friendly design and avoid scattering user-facing text throughout application logic.

Agricultural terms should be reviewed by competent speakers or agricultural specialists before being presented as authoritative translations.

Localization is a planned capability until the relevant translations have been implemented and tested.

## 11. Testing Procedure

Test each layer separately before performing an end-to-end test.

### Backend
- Authentication.
- Permissions.
- Image validation.
- Database operations.
- API response structure.
- Error handling.

### AI
- Input preprocessing.
- Class mapping.
- Expected output format.
- Unsupported images.
- Inference failures.
- Evaluation metrics.

### Flutter
- Form validation.
- Image selection.
- API integration.
- Loading and error states.
- Result display.
- Authentication behavior.

### End-to-End
Verify that a valid image can travel from the mobile client to the backend and inference component, then return a properly formatted result.

## 12. Troubleshooting Procedure

When a problem occurs:

1. Capture the exact error message.
2. Identify the failing component.
3. Check configuration and dependency versions.
4. Reproduce the problem with the smallest practical test.
5. Inspect relevant logs without exposing secrets.
6. Form a testable hypothesis.
7. Apply the smallest reasonable fix.
8. Rerun the relevant tests.
9. Document the root cause and resolution.

Do not apply multiple unrelated changes before determining the likely cause.

## 13. Documentation Procedure

When introducing a significant feature, update the relevant documentation.

Document:
- Purpose.
- Files and components involved.
- Dependencies.
- Configuration requirements.
- API contracts.
- Dataset and model details.
- Tests and evaluation results.
- Known limitations.

Keep documentation consistent with the current implementation.

## 14. Deployment Readiness Procedure

Before deployment, verify:
- Production configuration.
- Secret management.
- Database migrations and backups.
- Private media storage.
- Authentication and permissions.
- HTTPS configuration.
- Dependency compatibility.
- Logging and error handling.
- Model availability and resource requirements.
- Basic recovery procedures.

SQLite may be sufficient for an early prototype, but production database requirements should be evaluated against expected traffic, concurrency, and hosting constraints.

## 15. Completion Report

At the end of each development task, report:

1. What was completed.
2. Which files were created or modified.
3. Which commands and tests were run.
4. The actual test results.
5. Known limitations.
6. The recommended next step.

Never claim a feature is complete, tested, accurate, or deployed without evidence.
