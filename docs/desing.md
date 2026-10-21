# Agronia — System Design Document

## 1. Project Overview

**Project Name:** Agronia  
**Project Type:** AI-powered Agriculture Support Platform  
**Target Area:** Timor-Leste  
**Primary Goal:** Help farmers identify crop diseases, access agricultural information, and make better crop-management decisions using artificial intelligence.

Agronia is a digital agriculture platform designed for the needs of farmers in Timor-Leste. The platform will combine a mobile application, a web-based backend, and AI-assisted crop analysis.

The initial focus is crop disease identification from images. Future versions may include crop recommendations, agricultural weather information, pest identification, and local farming guidance.

## 2. Problem Statement

Farmers may face difficulties identifying crop diseases early, finding reliable agricultural information, and accessing expert assistance. These difficulties can affect crop health, productivity, and farming income.

Agronia aims to make preliminary crop disease information more accessible through an easy-to-use digital platform.

The system must not claim to replace agricultural experts. Its predictions are advisory and should communicate uncertainty clearly.

## 3. Target Users

### Farmers
- Submit crop images for analysis.
- View possible diseases and symptoms.
- Receive recommended next steps.
- Review previous analyses.

### Administrators
- Manage users and agricultural content.
- Monitor system activity.
- Manage disease information and educational resources.
- Review reports and system errors.

### Agricultural Experts (Future Phase)
- Review uncertain predictions.
- Validate agricultural recommendations.
- Contribute locally relevant information.

## 4. Core Features

### 4.1 User Authentication
- User registration and login.
- Secure password handling.
- Role-based access control.
- User profile management.

### 4.2 Crop Disease Detection
- Capture or upload a crop image.
- Select the crop type when necessary.
- Send the image to the AI inference service.
- Display the predicted disease or healthy classification.
- Show confidence information where technically justified.
- Provide symptoms and recommended next steps.
- Handle unsupported images and uncertain predictions safely.

### 4.3 Agricultural Knowledge Base
- Crop information.
- Disease descriptions and symptoms.
- Prevention and management guidance.
- Educational articles relevant to Timor-Leste.
- References and sources for agricultural recommendations.

### 4.4 Analysis History
- Store previous analyses for authenticated users.
- Display the submitted image, prediction, and analysis date.
- Allow users to revisit previous results.
- Apply appropriate access controls to uploaded images.

### 4.5 Administration Dashboard
- Overview of users and submitted analyses.
- Management of crop and disease information.
- Content moderation.
- Error and usage monitoring.

## 5. Technology Stack

### Mobile Application
- Flutter
- Dart
- HTTP client for communication with the backend
- Secure token storage where appropriate

### Backend
- Python
- Django
- Django REST Framework
- SQLite during early development
- PostgreSQL as a possible production database

### Artificial Intelligence
- Python
- PyTorch or TensorFlow, depending on the selected pretrained model
- Existing public crop disease datasets for initial experiments
- Pillow or an equivalent image-processing library

### Development and Deployment
- Git and GitHub
- Environment variables for configuration
- Automated tests
- A suitable application hosting service
- Separate development and production settings

Technology choices may be revised when compatibility, dataset quality, or deployment requirements justify a change.

## 6. High-Level Architecture

The system consists of four primary components.

1. **Flutter Client:** Provides the interface for farmers.
2. **Django REST API:** Handles authentication, requests, validation, and data management.
3. **AI Inference Service:** Loads the selected model and generates crop image predictions.
4. **Database and File Storage:** Stores users, analysis records, agricultural content, and permitted image files.

### Request Flow

1. A farmer selects or captures a crop image.
2. Flutter validates the file and sends it to the Django API.
3. Django checks authentication, file type, file size, and request validity.
4. The inference component processes the image.
5. The backend validates and formats the prediction.
6. The result is returned to the mobile application.
7. The analysis is saved when appropriate and authorized.

The AI model should be isolated behind a clear service interface so it can be replaced without redesigning the entire application.

## 7. AI Model Strategy

### Initial Approach
- Evaluate existing pretrained crop disease models and publicly available datasets.
- Confirm dataset licensing and permitted use.
- Identify supported crops and disease classes.
- Establish a baseline model before attempting fine-tuning.
- Evaluate performance on images representative of real farming conditions.

### Model Output
A prediction should include, where supported:
- Predicted class.
- Confidence score.
- Model version.
- Supported crop or disease category.
- A clear uncertainty message when the result is unreliable.

A confidence score is not automatically a measure of real-world correctness. It must not be presented as a guarantee.

### Dataset Limitations
Public datasets may contain images captured under controlled conditions that differ from farms in Timor-Leste. Local validation is required before making strong claims about accuracy or practical effectiveness.

## 8. Interface and Design Principles

The interface should be:
- Simple and accessible to farmers with different levels of digital literacy.
- Mobile-first and responsive.
- Clear, readable, and easy to navigate.
- Consistent across screens.
- Designed for low-bandwidth conditions where practical.

### Main Screens
1. Welcome and onboarding.
2. Login and registration.
3. Home dashboard.
4. Crop image submission.
5. Analysis loading and results.
6. Analysis history.
7. Agricultural knowledge.
8. User profile and settings.

### Visual Direction
Use a clean agricultural identity with natural green accents, neutral backgrounds, readable typography, and clear status indicators.

Avoid unnecessary animations, excessive gradients, and decorative elements that interfere with usability.

## 9. API Design Principles

The API should:
- Use versioned endpoints, such as `/api/v1/`.
- Return consistent JSON responses.
- Validate every incoming request.
- Apply authentication and permissions where required.
- Provide useful error messages without exposing internal exceptions.
- Document endpoints and expected response formats.

Exact endpoint definitions should be documented when implementation begins.

## 10. Security and Privacy

- Never commit secrets, API keys, or production credentials.
- Use environment variables for sensitive configuration.
- Validate uploaded images and enforce upload limits.
- Restrict access to private analysis records.
- Apply authentication and authorization consistently.
- Avoid storing unnecessary personal information.
- Use HTTPS in production.
- Keep dependencies updated and review their security implications.

## 11. Reliability and Performance

- Resize images when appropriate before inference.
- Avoid blocking unrelated API requests during expensive processing.
- Handle model-loading failures and timeouts.
- Provide understandable error states.
- Keep database queries efficient.
- Consider offline educational content in a future version.
- Do not advertise offline AI inference until it has been implemented and tested.

## 12. Testing and Quality Assurance

Testing should cover:
- Authentication and permissions.
- API request validation.
- Image upload and invalid file handling.
- AI inference integration.
- Prediction formatting and uncertainty handling.
- Database operations.
- Mobile navigation and API error states.
- Performance under realistic conditions.

AI evaluation should include per-class precision, recall, F1-score, confusion matrices, and suitable validation data.

## 13. Development Roadmap

### Phase 1 — Foundation
- Establish the repository structure.
- Finalize documentation and development conventions.
- Set up the Python and Flutter environments.
- Confirm dependency compatibility.

### Phase 2 — Backend
- Create the Django project and REST API.
- Implement authentication and data models.
- Add agricultural content management.
- Write backend tests.

### Phase 3 — AI Prototype
- Inspect candidate datasets.
- Select a baseline model.
- Build an inference pipeline.
- Evaluate the model and document its limitations.

### Phase 4 — Mobile Application
- Create the main Flutter screens.
- Integrate authentication.
- Implement image upload and prediction results.
- Add analysis history.

### Phase 5 — Validation
- Test the complete application.
- Collect feedback from farmers or agricultural specialists.
- Validate supported crops and diseases under local conditions.
- Fix usability, performance, and security issues.

### Phase 6 — Deployment
- Prepare production configuration.
- Deploy the backend and model.
- Configure storage and database backups.
- Document installation, maintenance, and recovery procedures.

## 14. Success Criteria

Agronia should be considered ready for an initial demonstration when:
- A user can submit a valid crop image.
- The backend can process the request and return a valid result.
- Unsupported inputs are handled safely.
- Results clearly communicate their limitations.
- Authentication and analysis access controls work correctly.
- The mobile application handles network and server errors.
- The prototype can be demonstrated reproducibly.

Claims about agricultural impact or model accuracy must be supported by actual evaluation results.

## 15. Future Improvements

Potential future capabilities include:
- More crop types relevant to Timor-Leste.
- Tetum, Portuguese, and Indonesian language support.
- Offline access to selected educational materials.
- Local agricultural expert review.
- Weather information and seasonal farming guidance.
- Pest identification and crop-management support.

Future capabilities must remain separate from features that are already implemented.
