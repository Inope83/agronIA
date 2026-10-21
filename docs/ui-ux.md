# Agronia — UI/UX Design Specification

**Project:** Agronia  
**Purpose:** AI-powered agriculture assistance for Timor-Leste  
**Platform:** Flutter mobile application  
**Backend:** Django REST Framework  
**Document Status:** Design Specification  
**Version:** 1.0

---

## 1. Overview

Agronia is an AI-powered agriculture application designed to help farmers in Timor-Leste identify possible crop diseases from plant images and access useful agricultural information.

The user interface must be simple, accessible, reliable, and suitable for users with different levels of digital literacy.

The design must prioritize practical agricultural needs rather than unnecessary visual effects or complicated navigation.

### Primary Objectives

- Help farmers submit crop images for AI analysis.
- Present preliminary disease predictions in understandable language.
- Provide practical recommendations for the next steps.
- Make agricultural information easy to discover.
- Support users with slow or unstable internet connections.
- Create a consistent and professional mobile experience.

## 2. Target Users

### Primary Users: Farmers

Farmers need to identify potential crop problems, understand the results, and learn what actions they can take.

### Secondary Users: Agricultural Students and Extension Workers

These users may use Agronia to explore crop diseases, review analysis results, and access agricultural learning materials.

### Future Users: Administrators

Administrators may manage agricultural information, supported crops, educational resources, and application content through a separate management interface.

## 3. Design Principles

### 3.1 Simplicity

- Use familiar icons with text labels.
- Keep navigation short and predictable.
- Show one primary action per screen whenever possible.
- Avoid unnecessary menus and technical terminology.
- Use clear instructions for every important task.

### 3.2 Accessibility

- Use readable text and sufficient contrast.
- Do not communicate important information through color alone.
- Provide visible labels for buttons and form fields.
- Use sufficiently large touch targets, preferably around 48 × 48 logical pixels.
- Support text scaling and different screen sizes.

### 3.3 Mobile-First Design

The mobile application is the primary interface. Screens must work on smaller Android devices before being adapted to larger screens.

### 3.4 Reliability

- Display loading progress during analysis.
- Explain network errors in plain language.
- Preserve user input when possible after a failure.
- Never display fabricated analysis results.
- Clearly distinguish preliminary AI predictions from confirmed diagnoses.

### 3.5 Local Relevance

Agronia is intended for users throughout Timor-Leste. Crop information, terminology, and recommendations must be reviewed for local relevance.

Potential interface languages include Tetum, Portuguese, and Indonesian. Language support must be implemented and verified before being presented as available.

## 4. Visual Identity and Design System

### 4.1 Color Palette

Use a green-and-white visual identity associated with agriculture, growth, and clarity.

| Token | Proposed color | Usage |
|---|---|---|
| Primary Green | `#2E7D32` | Main buttons, active navigation, primary actions |
| Dark Green | `#1B5E20` | Headings, emphasis, selected elements |
| Light Green | `#E8F5E9` | Soft backgrounds and informational cards |
| White | `#FFFFFF` | Main surfaces and cards |
| Background | `#F7F9F7` | Main application background |
| Main Text | `#212121` | Primary text |
| Secondary Text | `#616161` | Descriptions and supporting text |
| Border | `#E0E0E0` | Dividers and input borders |
| Warning | `#F9A825` | Cautions and attention notices |
| Error | `#C62828` | Failed operations and critical errors |
| Success | `#2E7D32` | Successful operations |

These values are proposed design tokens. Check contrast and usability before implementation, especially for text placed over colored backgrounds.

### 4.2 Typography

Use a clean, readable sans-serif typeface supported by Flutter and the target devices.

Recommended hierarchy:

- **Display:** 28–32 sp, for major introductory headings.
- **Page title:** 22–24 sp.
- **Section heading:** 18–20 sp.
- **Body text:** 14–16 sp.
- **Supporting text:** 12–14 sp.
- **Button labels:** 14–16 sp, medium or semibold weight.

Text sizes must remain usable when users increase their device's font size.

### 4.3 Spacing

Use a consistent spacing scale based on multiples of four:

- 4: very small spacing.
- 8: compact spacing.
- 12: related elements.
- 16: standard content spacing.
- 24: section spacing.
- 32: major section separation.

Maintain consistent horizontal page padding, normally 16–20 logical pixels on mobile.

### 4.4 Shapes and Elevation

- Buttons: rounded corners, approximately 10–12 px.
- Cards: rounded corners, approximately 12–16 px.
- Input fields: rounded corners, approximately 10–12 px.
- Use subtle borders or shadows.
- Avoid excessive gradients, decorative effects, and unnecessary animation.

### 4.5 Icons and Images

Use a consistent icon family throughout the application.

Icons should have recognizable meanings and text labels where the action may be unfamiliar. Plant images must be relevant to the content and must not be presented as actual diagnostic evidence unless they belong to the relevant analysis.

## 5. Navigation Structure

The proposed main navigation contains four destinations:

1. **Home** — overview and primary actions.
2. **Analyze** — submit a crop image for analysis.
3. **History** — review previous analyses, when history storage is implemented.
4. **Learn** — browse agricultural educational resources.

Use a bottom navigation bar on mobile.

Account settings, language preferences, help, and application information can be accessed through the profile or settings area.

Navigation items must lead to implemented screens. Until a feature is available, it must not be presented as a working function.

## 6. Screen Specifications

### 6.1 Splash Screen

**Purpose:** Introduce Agronia while the application initializes.

Elements:

- Agronia logo or temporary wordmark.
- Short agriculture-related tagline.
- Minimal loading indicator when initialization takes time.

The splash screen must not remain visible indefinitely if initialization fails.

### 6.2 Home Screen

**Purpose:** Help users quickly access the main features.

Recommended layout:

1. Agronia branding and profile or settings access.
2. Greeting or short introductory message.
3. Primary card: **Analyze Crop Image**.
4. Quick access to agricultural learning materials.
5. Recent analysis summary, when available.
6. Bottom navigation.

The main analysis action must be visually prominent without overwhelming other content.

Avoid showing invented statistics, fake recent results, or unsupported claims about crop health.

### 6.3 Crop Analysis Screen

**Purpose:** Collect the information needed to analyze a crop image.

Required interface elements:

- Page title and short instructions.
- Image selection from the gallery.
- Camera capture option, if camera functionality is implemented.
- Image preview.
- Crop selection.
- Optional description of visible symptoms.
- Submit button.

The application should explain that clear images with good lighting and visible affected areas usually provide more useful visual information.

Before submission, validate the selected file type, file size, and other requirements established by the backend.

If a required crop selection is missing, explain what the user needs to provide.

### 6.4 Analysis Loading Screen

**Purpose:** Explain that the analysis is in progress.

Elements:

- Loading indicator.
- Short message describing the current operation.
- Clear indication that the application is processing the submitted image.

The interface must distinguish between uploading an image and analyzing it when the backend provides those states.

If processing takes longer than expected, provide a helpful message instead of displaying an endless spinner without explanation.

Do not simulate a successful result when the server has failed or returned no prediction.

### 6.5 Analysis Result Screen

**Purpose:** Present the model output in an understandable format.

Recommended information hierarchy:

1. Submitted crop image.
2. Crop name, if known.
3. Predicted disease or condition.
4. Confidence score, only if returned and appropriately calibrated.
5. Explanation of the prediction.
6. Practical next steps supported by reviewed agricultural information.
7. Important uncertainty and safety notice.
8. Option to return home or save the result, if supported.

Example of the intended presentation:

**Possible result:** Suspected leaf disease

**What this means:** The AI identified visual patterns that may be associated with this condition.

**Recommended next step:** Inspect other affected leaves and compare the symptoms with verified agricultural guidance. Seek advice from an agricultural extension worker if the problem persists or spreads.

**Important notice:** This is a preliminary AI prediction, not a confirmed diagnosis.

The example above is illustrative. Actual disease names, explanations, confidence values, and recommendations must come from validated application data or model output.

If the model cannot make a reliable prediction, the interface must communicate that limitation instead of forcing a disease label.

### 6.6 Analysis History Screen

**Purpose:** Allow users to review previous analysis records.

Each item may display:

- Thumbnail image.
- Crop name.
- Predicted condition.
- Analysis date.
- Processing status, if relevant.

Users should be able to open a record to review its details.

History functionality depends on an implemented storage strategy. If the feature is not available, do not show fabricated records.

### 6.7 Learn Screen

**Purpose:** Provide agricultural knowledge that does not depend on an AI prediction.

Potential content categories:

- Crop cultivation.
- Common crop diseases.
- Pest management.
- Soil and watering practices.
- Harvest and post-harvest guidance.

Content must be reviewed for accuracy and local relevance. Each resource should have a clear title, summary, category, and source where appropriate.

For slow connections, use lightweight pages and compressed images. Offline access can be added in a later development phase.

### 6.8 Settings Screen

Potential settings:

- Preferred language.
- Text or accessibility preferences where supported.
- Privacy information.
- Help and feedback.
- Application version.

Only display controls that actually work.

## 7. User Flow

### 7.1 Main Analysis Flow

1. User opens Agronia.
2. User selects **Analyze Crop Image**.
3. User selects or captures a crop image.
4. User selects the crop type.
5. User reviews the image and submitted information.
6. User submits the analysis request.
7. Agronia validates the input.
8. The application uploads the image to the Django backend.
9. The backend processes the request using the configured AI model.
10. The backend returns a result or an appropriate error.
11. Agronia displays the result, including uncertainty where necessary.
12. The user reviews the recommended next steps.
13. The user returns home or saves the result if supported.

### 7.2 Failure Flow

If image selection, upload, or model processing fails:

1. Display a clear error message.
2. Explain the likely cause when it is known.
3. Preserve the selected image when possible.
4. Offer a relevant recovery action, such as trying again.
5. Avoid presenting an unsuccessful request as a completed analysis.

### 7.3 Uncertain Prediction Flow

If the model cannot provide a sufficiently reliable prediction:

1. Display an uncertain or inconclusive result.
2. Explain that the image may not contain enough useful information.
3. Suggest taking a clearer image when appropriate.
4. Offer general, verified guidance or recommend expert review.
5. Do not present an unsupported disease diagnosis.

### 7.4 Learning Flow

1. User opens Learn.
2. User browses or searches available resources.
3. User selects a topic.
4. Agronia displays the educational content.
5. User returns to the resource list or home screen.

## 8. Network and Offline Experience

Agronia is intended for use throughout Timor-Leste, where connectivity can vary.

The initial architecture may require an internet connection to upload images and obtain server-side AI predictions.

The interface should:

- Detect and communicate network-related failures.
- Show upload and processing progress when available.
- Avoid unnecessary image uploads.
- Compress images appropriately without destroying important visual details.
- Retry requests only under a defined, safe retry policy.
- Avoid silently submitting the same analysis multiple times.
- Preserve recoverable user input when possible.

Offline access to educational resources and offline AI inference are separate capabilities. Neither should be advertised until implemented and tested.

## 9. Error and Empty States

Every major screen must define its loading, success, empty, and failure states.

| Situation | Expected interface response |
|---|---|
| No image selected | Explain how to select an image |
| Unsupported image | Explain the accepted file formats |
| Image too large | Explain the size limit and how to reduce the image |
| No internet connection | Explain that the request cannot currently reach the server |
| Upload failed | Offer a retry while preserving the image when possible |
| AI processing failed | Explain that analysis could not be completed |
| Uncertain prediction | Clearly communicate the uncertainty |
| No history | Explain that no saved analyses are available |
| No learning content | Show an appropriate empty state |
| Server unavailable | Provide a friendly message and recovery option |

Error messages should be written for ordinary users rather than developers. Technical details may be recorded in development logs without exposing sensitive information in the interface.

## 10. Accessibility and Localization

- Use simple, direct language.
- Provide meaningful labels for interactive elements.
- Maintain readable contrast.
- Support larger text where possible.
- Avoid relying exclusively on color or icons.
- Ensure important actions are easy to reach.
- Keep layouts usable on smaller devices.
- Prepare text for localization rather than embedding every label directly in screen layouts.

Tetum, Portuguese, and Indonesian may be considered for localization. Translations of agricultural terminology and disease information must be reviewed before release.

## 11. Privacy and User Trust

Crop images and analysis records must be handled according to the application's privacy policy.

The design must:

- Explain when an image will be uploaded to a server.
- Avoid requesting unnecessary personal information.
- Provide clear feedback when a request is submitted.
- Avoid exposing private image URLs or internal server errors.
- Communicate model limitations honestly.
- Never claim that an AI prediction is guaranteed to be correct.

Any future account, history, or image-retention feature must follow a defined data-handling policy.

## 12. UI Component Inventory

The application should maintain consistent reusable components for:

- Primary and secondary buttons.
- Text input fields.
- Crop selection controls.
- Image selection and preview areas.
- Information cards.
- Result cards.
- Confidence and uncertainty indicators.
- Loading indicators.
- Error messages.
- Empty-state illustrations or icons.
- Navigation items.
- Confirmation dialogs.
- Educational resource cards.

Components should share the same color, typography, spacing, and accessibility rules.

## 13. Responsive Design

### Small Mobile Screens

- Use a single-column layout.
- Keep primary actions visible.
- Allow vertical scrolling when necessary.
- Prevent buttons and text from overflowing.

### Larger Mobile Screens

- Use additional whitespace where appropriate.
- Keep content width readable.
- Maintain the same navigation hierarchy.

### Tablets and Larger Displays

- Consider wider cards or a two-column layout where useful.
- Preserve the mobile application's visual hierarchy.
- Do not stretch text and forms across excessively wide areas.

Responsive behavior must be tested on real or emulated Android screen sizes.

## 14. Design Acceptance Criteria

The UI/UX specification is ready for implementation when:

- Every planned screen has a clear purpose.
- Navigation between screens is defined.
- The main crop analysis flow is documented.
- Loading, failure, and uncertain-result states are defined.
- Colors, typography, spacing, and component styles are consistent.
- Mobile accessibility and responsiveness are considered.
- Network limitations are communicated honestly.
- Proposed features are distinguished from implemented functionality.
- AI predictions are presented as preliminary rather than definitive diagnoses.

## 15. Implementation Notes

This document defines the intended design and behavior. It does not mean that the screens or features already exist.

Before implementation, review this specification alongside the project's `architecture.md`, `api.md`, `security.md`, and `ai-model.md`.

When implementation begins, build the main navigation and screen layouts first, then connect the analysis flow to the Django API. Integrate AI output only after the backend response format and model behavior have been established.

**End of document.**