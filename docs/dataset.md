# Agronia — Dataset Research and Management

## 1. Purpose

This document defines how Agronia will discover, assess, select, prepare, and evaluate datasets for crop disease identification.

No dataset is considered selected, downloaded, or approved merely because it is listed as a candidate.

## 2. Initial Objective

Identify a suitable dataset for a computer vision baseline that classifies selected crop disease categories.

The initial supported crop must be selected after evaluating dataset availability, disease classes, technical feasibility, and agricultural relevance to Timor-Leste.

## 3. Candidate Sources

The following sources may be investigated:

### PlantVillage
A widely used research dataset for plant disease classification.

Official project website: https://plantvillage.psu.edu/

### Kaggle
A platform hosting datasets uploaded by different publishers.

Website: https://www.kaggle.com/datasets

Each candidate's original source, publisher, license, and terms must be reviewed individually.

### Research repositories
University repositories, research publications, and recognized agricultural institutions may provide additional datasets.

No candidate should be assumed to be suitable or legally reusable without checking its documentation.

## 4. Dataset Selection Criteria

Evaluate each candidate using the following criteria:

| Criterion | Questions |
|---|---|
| Source | Who created or published the dataset? |
| License | What uses, redistribution, and modifications are permitted? |
| Crop coverage | Does it include the intended crop? |
| Disease coverage | Are the relevant diseases represented? |
| Class balance | Are some classes significantly underrepresented? |
| Image quality | Are images clear and correctly labeled? |
| Image conditions | Do the images resemble real field conditions? |
| Label quality | Are labels supported by reliable documentation? |
| Duplicates | Are repeated or near-identical images present? |
| Local relevance | Is there evidence of relevance to Timor-Leste? |
| Technical usability | Can the dataset be processed with available resources? |

## 5. Dataset Comparison Record

Create one record for each candidate.

| Field | Description |
|---|---|
| Dataset name | Official or published name |
| Source URL | Original source |
| Publisher | Organization or contributor |
| License | Verified usage terms |
| Version | Version or release identifier |
| Download status | Not reviewed, available, downloaded, or unavailable |
| Supported crops | Documented crop classes |
| Disease classes | Documented labels |
| Class distribution | Image counts where available |
| Format | Image formats and annotation structure |
| Limitations | Known quality and coverage issues |
| Decision | Accept, reject, or investigate further |

Populate these fields only after inspecting the actual dataset documentation.

## 6. Label Compatibility

Different datasets and models may use different names for the same or similar diseases.

Before combining labels:
- Review the original label definitions.
- Confirm that labels have equivalent meanings.
- Preserve original labels for traceability.
- Document any mapping.
- Obtain expert input when disease distinctions are uncertain.

Do not merge visually or scientifically distinct categories just to simplify the model.

## 7. Data Preparation

The preparation workflow may include:

1. Inspect the downloaded archive.
2. Verify image readability.
3. Review labels and directory structure.
4. Identify duplicate or corrupted files.
5. Check class counts.
6. Standardize supported image formats where necessary.
7. Define deterministic preprocessing.
8. Record excluded files and reasons.
9. Prepare training, validation, and test splits.
10. Document the final dataset version.

Never silently remove a large portion of the data without recording why.

## 8. Data Splitting and Leakage Prevention

The dataset should be separated into training, validation, and test subsets.

- Training data is used to fit model parameters.
- Validation data is used for model selection and tuning.
- Test data is reserved for final evaluation.

Avoid placing duplicate images, near-duplicate images, or images from the same source group across different splits when that would lead to misleading results.

Where possible, use a split strategy that reflects the intended deployment setting.

Do not repeatedly tune the model against the final test set.

## 9. Augmentation

Possible training-time augmentation includes:
- Small rotations.
- Horizontal or vertical transformations when biologically appropriate.
- Moderate brightness or contrast variation.
- Carefully selected cropping and scaling.

Augmentation must not alter disease-defining symptoms or create unrealistic examples.

Validation and test images should receive only the preprocessing required by the model, not random training augmentation.

## 10. Timor-Leste Local Validation

Public dataset results do not establish performance under local farming conditions.

When practical and with appropriate permission, future validation should include images representing:
- Different lighting conditions.
- Different camera devices.
- Field backgrounds.
- Relevant local crop varieties.
- Different stages of visible symptoms.
- Healthy crops and non-target images.

Record the collection context without unnecessarily identifying individual farmers or revealing sensitive location information.

Labels for field images should be reviewed by a qualified agricultural specialist when feasible.

## 11. Data Privacy and Licensing

Before using any image collection:
- Review its license and terms.
- Confirm whether commercial or research use is allowed for the intended project.
- Check redistribution and attribution requirements.
- Obtain appropriate consent for newly collected personal or identifiable content.
- Avoid collecting unnecessary personal information.
- Protect access to non-public images.

A dataset being publicly downloadable does not automatically make it unrestricted.

## 12. Dataset Versioning

For each approved dataset version, record:
- Source and version.
- Retrieval date.
- License.
- Class definitions.
- Preparation steps.
- Split strategy.
- File counts and class counts.
- Checksums or another suitable integrity record where practical.
- Known limitations.

Do not commit large datasets to Git unless the repository's storage and licensing arrangements explicitly support that approach.

## 13. Required Deliverables

Before model training begins, produce:
- Dataset comparison.
- License review.
- Supported class list.
- Data preparation procedure.
- Split strategy.
- Data quality report.
- Known limitations.
- Selection rationale.

## 14. Current Status

No specific dataset has been approved by this document.

The next step is to investigate candidate datasets and record evidence before deciding which crop and disease classes Agronia should support initially.
