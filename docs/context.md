# Agronia — Project Context

## 1. Purpose

Agronia is a planned AI-assisted agriculture platform for Timor-Leste.

This document defines the problem, intended users, objectives, assumptions, constraints, and boundaries that should guide project decisions.

It does not claim that the proposed problems have already been validated through field research.

## 2. Geographic Scope

The intended coverage is all of Timor-Leste, including rural and urban farming communities across the country's municipalities.

The initial prototype may support only a limited number of crops and diseases. Nationwide project scope does not mean nationwide model validation has already been achieved.

## 3. Problem Definition

Potential challenges that Agronia intends to investigate include:

- Difficulty recognizing crop disease symptoms.
- Limited access to timely agricultural information.
- Differences between general online information and local farming conditions.
- Uncertainty about where to seek further advice when symptoms are unclear.
- Limited availability of digital agricultural support in appropriate local languages.

These are problem hypotheses that require confirmation through farmer interviews, agricultural literature, or expert consultation.

## 4. Target Users

### Primary users: Farmers

Expected needs:
- Simple instructions.
- A straightforward way to submit crop images.
- Understandable results.
- Practical prevention and management information.
- Clear explanations when the AI cannot provide a reliable answer.

### Secondary users: Administrators

Expected needs:
- Manage agricultural content.
- Review user activity within authorized limits.
- Maintain crop and disease information.
- Monitor system errors and service availability.

### Future users: Agricultural specialists

Potential responsibilities:
- Validate disease information.
- Review uncertain predictions.
- Contribute locally relevant guidance.
- Help assess model performance in real farming environments.

These roles are proposed for design purposes. Their actual workflows require further validation.

## 5. Initial Use Case

A farmer observes unusual symptoms on a crop and wants preliminary guidance.

The intended workflow is:

1. Open Agronia.
2. Select or capture a crop image.
3. Select the crop type if required.
4. Submit the image.
5. Receive a possible classification if the image and crop class are supported.
6. Review relevant symptoms and guidance.
7. Seek expert assistance if the result is uncertain or the problem is serious.

Agronia should communicate uncertainty rather than force a disease classification for every image.

## 6. Objectives

### Primary objectives
- Develop a maintainable AI agriculture prototype.
- Investigate crop disease identification using computer vision.
- Make agricultural information easier to access.
- Evaluate technical feasibility and usefulness.

### Secondary objectives
- Design for users with different levels of digital literacy.
- Plan support for relevant Timor-Leste languages.
- Explore low-bandwidth and offline educational access.
- Establish a pathway for local expert validation.

## 7. Initial Scope

The first prototype should prioritize:
- One clearly defined crop disease identification workflow.
- A documented set of supported classes.
- A baseline model and evaluation process.
- A Django API.
- A Flutter client.
- Clear error and uncertainty messages.
- Basic tests and technical documentation.

The first crop and disease classes will be selected after reviewing available datasets and obtaining appropriate agricultural input.

## 8. Out of Scope for the Initial Prototype

Unless explicitly added to the agreed scope, the first version will not promise:
- Identification of every crop disease.
- Guaranteed diagnosis or treatment.
- Automatic pesticide prescriptions.
- Nationwide field accuracy.
- Fully offline AI inference.
- Real-time agricultural expert consultations.
- Live weather integration.
- Proven improvements in crop yields or farmer income.

## 9. Constraints and Risks

### Data limitations
Public datasets may not represent local varieties, symptoms, backgrounds, or farming conditions.

### Infrastructure
Internet reliability, device capabilities, and hosting resources may vary across intended users.

### Expertise
Agricultural guidance should be reviewed by appropriate specialists before being presented as authoritative.

### Development capacity
The initial project may be developed by a small team or an individual. The design should therefore favor simple, testable components.

### Language
Technical translations and agricultural terminology may require review by competent local speakers and specialists.

## 10. Assumptions to Validate

- Farmers consider image-based disease guidance useful.
- Suitable public datasets exist for the selected initial crop.
- The chosen model can be integrated with reasonable hardware resources.
- The target users can access compatible mobile devices.
- Local agricultural specialists or trusted references can support validation.
- The proposed interface is understandable to intended users.

These assumptions must be investigated rather than treated as established facts.

## 11. Success Indicators

Initial technical indicators:
- Valid image requests can be processed.
- The model returns documented output classes.
- Unsupported inputs are handled safely.
- Tests verify important API and permission behavior.
- The application displays results and errors clearly.

Future field indicators:
- User comprehension.
- Farmer satisfaction.
- Expert agreement with predictions.
- Performance across relevant crops and locations.
- Practical usefulness of the recommended next steps.

Field outcomes must be measured before impact claims are made.

## 12. Guiding Principle

Agronia should be developed as a support tool for farmers, not as a replacement for agricultural expertise. Reliability, transparency, local relevance, and maintainability take priority over adding features that have not been validated.
