# Agronia — AI Model Design and Evaluation

## 1. Purpose

This document defines the planned approach for selecting, integrating, evaluating, and maintaining the computer vision model used by Agronia.

An MVP baseline has been trained and evaluated: MobileNetV2 for four rice leaf classes, with 84.59% accuracy on a held-out test split. Section 15 records the configuration, metrics, artifacts, and limitations. The model has not been validated on local farm images from Timor-Leste, so its field performance is unknown.

## 2. Initial AI Objective

The first AI objective is to evaluate whether a computer vision model can provide useful preliminary classification of selected crop disease categories from images.

The initial task is image classification, unless dataset or user requirements establish that object detection or segmentation is more appropriate.

Image classification assigns a class to an image. It does not necessarily locate disease symptoms within the image.

## 3. Model Selection

Investigate existing pretrained models before considering training from scratch.

Candidate approaches may include:
- Transfer learning with a pretrained image classification network.
- Fine-tuning a model on a suitable crop disease dataset.
- Training a smaller model if compute constraints require it.

Potential frameworks include PyTorch and TensorFlow.

Do not select a framework or architecture until compatibility, licensing, model quality, and resource requirements have been evaluated.

## 4. Model Selection Criteria

Assess:
- Compatibility with the dataset's label structure.
- Baseline performance.
- Per-class performance.
- Model size.
- Memory requirements.
- Inference latency.
- Hardware compatibility.
- Licensing and permitted use.
- Ease of deployment and maintenance.

A model with high benchmark accuracy may still be unsuitable for real farm images.

## 5. Model Input Contract

The model's input contract must specify:
- Accepted image formats.
- Expected image dimensions.
- Color channel ordering.
- Pixel normalization.
- Any required cropping or resizing.
- Supported input conditions.

These values must be obtained from the selected model and its preprocessing requirements rather than guessed.

## 6. Prediction Output

The inference component should return a structured internal result containing, where applicable:

- Predicted class identifier.
- Human-readable class label.
- Model confidence score.
- Model version.
- Supported status or uncertainty indicator.

The API layer may add explanatory information from the agricultural knowledge base.

The output must distinguish a valid prediction from an error or unsupported input.

## 7. Uncertainty Handling

A model should not be forced to produce a trustworthy disease diagnosis for every image.

Possible uncertainty cases include:
- Unsupported crop.
- Unknown disease category.
- Blurry or poorly exposed image.
- Image that does not contain a crop.
- Model failure.
- Low or poorly calibrated confidence.

An uncertainty threshold should be chosen using validation data and a documented evaluation method.

Softmax confidence alone does not prove that a prediction is correct or that the model can recognize unfamiliar classes.

## 8. Training and Fine-Tuning Workflow

If fine-tuning is justified:

1. Confirm dataset license and quality.
2. Freeze a documented dataset version.
3. Establish training, validation, and test splits.
4. Define preprocessing and augmentation.
5. Record the initial model and weights.
6. Configure reproducible training settings.
7. Train using available hardware.
8. Monitor validation performance.
9. Select a model using predefined criteria.
10. Evaluate once on the held-out test set.
11. Record the model artifact and its metadata.
12. Document known limitations.

Training from scratch should not be the default approach without a clear technical justification.

## 9. Evaluation Metrics

Report appropriate metrics, including:
- Accuracy, where meaningful.
- Precision per class.
- Recall per class.
- F1-score per class.
- Macro-averaged F1-score where appropriate.
- Confusion matrix.
- Per-class sample counts.
- Inference latency and resource use.

For imbalanced datasets, aggregate accuracy alone may conceal poor performance on underrepresented diseases.

Report the dataset and split used for every metric.

## 10. Local Validation

Before making claims about effectiveness in Timor-Leste, evaluate the model on suitable local data.

A local validation plan should consider:
- Relevant crop varieties.
- Real farm backgrounds.
- Different lighting conditions.
- Different devices.
- Disease stages.
- Healthy and unsupported examples.

Where possible, use expert-reviewed labels and an evaluation process that avoids leakage from training data.

If local validation has not occurred, clearly state that limitation.

## 11. Model Artifact Management

For each model version, record:
- Model name and architecture.
- Framework and version.
- Weight source and license.
- Dataset version.
- Supported classes.
- Preprocessing configuration.
- Evaluation metrics.
- Date of evaluation.
- Known failure cases.
- Artifact checksum where practical.

Model weights should not be confused with the source code or dataset. Each may have different license conditions.

## 12. Integration with the Backend

The inference layer is a separate FastAPI service in `ai/` (ADR-017). Django
calls it over HTTP and does not import model code or weights.

Request contract:

- `POST {AI_SERVICE_URL}/predict`
- `multipart/form-data` with a single image field named `file`
- Accepted formats must match the backend validators (JPG/PNG, maximum size
  configured by `DJANGO_MAX_UPLOAD_SIZE_MB`).

Successful response (`200`):

```json
{
  "status": "ok",
  "prediction": {
    "class_id": "padi-blast",
    "confidence": 0.91,
    "model_version": "model-version-identifier"
  },
  "message": "Short explanation for the user."
}
```

Failure response (`503`):

```json
{
  "detail": {
    "error": {
      "code": "model_unavailable",
      "message": "Model is not loaded."
    }
  }
}
```

Backend behaviour:

- AI service unreachable or timed out: `503 service_unavailable`.
- AI service reports `model_unavailable`: `503 model_unavailable`.
- Invalid response, invalid confidence, or a `class_id` that is not a
  registered `Disease.code`: `502 inference_failed`.
- Every failure is stored as `status: "failed"` with no prediction data.

`class_id` values must match the `code` of an active `Disease` record. The
model should not be loaded repeatedly for every request unless required by
the chosen serving architecture.

## 13. Performance and Deployment

Before deployment, measure:
- Model memory use.
- Initialization time.
- Per-image inference latency.
- Concurrent request behavior.
- Expected hosting cost.
- Compatibility with the intended runtime.

GPU use should not be assumed. The baseline should be tested on the hardware realistically available for development and deployment.

## 14. Safety and Agricultural Limitations

Agronia should:
- Describe predictions as preliminary guidance.
- Avoid guarantees of diagnosis.
- Avoid unsupported treatment instructions.
- Present relevant warnings for uncertain results.
- Recommend specialist review when appropriate.
- Distinguish model output from expert-verified information.

## 15. Implemented Baseline (MVP)

**Status (2026-10-22):** trained, evaluated on a held-out test split, and wired
into the FastAPI service. Not yet validated on local field images.

### Model and runtime

- Architecture: MobileNetV2 (ImageNet weights) with global average pooling,
  dropout, and a four-class softmax head.
- Model version: `rice-mobilenetv2-v1`.
- Input: RGB, 224x224, pixel scale 0-255. `preprocess_input` is inside the
  model; augmentation layers are inactive during inference.
- Runtime: Keras 3.15.1 with the PyTorch 2.14.1 CPU backend, because
  TensorFlow has no wheel for the available Python 3.14 environment.
- Artifact: `ai/weights/agronia_rice_mobilenetv2.keras` (about 21 MB, not
  committed). Class registry: `ai/classes.json`.
- Service: loads the model at startup from `AI_MODEL_PATH`; measured inference
  latency was about 100 ms per image on the development machine.

### Dataset and splits

- Source: Rice Leaf and Crop Disease Detection Dataset, Labib et al. (2024),
  DOI `10.17632/g7tcwvshff.1`, CC BY 4.0.
- Only original/raw images were used; augmented copies and the unsupported
  `Rice` class were excluded.
- 1,923 original images were found; 63 exact duplicates were removed, leaving
  1,860 images:
  - Bacterial Leaf Blight: 262
  - Healthy Leaf: 771
  - Rice Blast: 590
  - Tungro: 237
- Stratified 70/15/15 train/validation/test split with seed 42. SHA-256 hashes
  were checked to prevent the same image appearing in more than one split.
- Test set: 279 images.

### Training configuration

- Stage 1: frozen MobileNetV2 base, 12 epochs, Adam at 1e-3, class weights,
  augmentation (horizontal flip, small rotation/zoom/contrast), early stopping.
- Stage 2: unfroze the last 30 base layers (batch normalization kept frozen),
  8 epochs, Adam at 1e-5, early stopping and learning-rate reduction.
- Batch size 32; selection monitored validation accuracy.
- The exact notebook is `ai/notebooks/train_rice_colab.ipynb`.

### Held-out test metrics

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Bacterial Leaf Blight | 0.7805 | 0.8000 | 0.7901 | 40 |
| Healthy Leaf | 0.9262 | 0.9826 | 0.9536 | 115 |
| Rice Blast | 0.8193 | 0.7640 | 0.7907 | 89 |
| Tungro | 0.6970 | 0.6571 | 0.6765 | 35 |

- Overall accuracy: 0.8459 (84.59%).
- Test loss: 0.3928.
- Macro F1: 0.8027; weighted F1: 0.8434.
- Confusion matrix (rows = actual, columns = predicted, class order above):
  `[[32, 2, 5, 1], [1, 113, 1, 0], [7, 5, 68, 9], [1, 2, 9, 23]]`.
- Tungro is the weakest class; nine Tungro images were predicted as Rice
  Blast, and nine Rice Blast images as Tungro.

Full results are in `ai/evaluation/metrics.json`, with the confusion matrix and
training curves as PNG files and the exact split in `ai/evaluation/splits.csv`.

### Known limitations

- The dataset is not from Timor-Leste. Accuracy on local varieties,
  backgrounds, lighting, devices, and disease stages is unknown.
- The model always chooses one of four classes. It cannot yet reject
  non-rice images, unsupported crops, or images without visible symptoms.
- Softmax confidence is not calibrated; a confidence threshold has not been
  selected from validation data.
- The healthy class may not represent all healthy conditions or nutrient
  deficiencies.
- `padi-sehat` is a healthy sentinel, not a disease. The backend `Disease`
  model does not yet have an `is_healthy` flag, so the UI must not present it
  as a disease.
- The dataset is CC BY 4.0 and requires attribution when redistributed.

### Next steps

1. Validate on expert-labelled local rice images from Timor-Leste.
2. Add unsupported/non-rice detection or an abstention rule and calibrate the
   confidence threshold.
3. Seed backend `Crop`/`Disease` records whose codes match `ai/classes.json`.
4. Collect user and agricultural-expert feedback before expanding scope.
5. Train a separate corn model only after the rice workflow is validated.
