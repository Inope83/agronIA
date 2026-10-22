# Agronia AI Service

Service terpisah untuk inference, training, dan eksperimen AI.

## Struktur
- `service/` - FastAPI service untuk inference
- `inference/` - Logic preprocessing & inference
- `weights/` - File bobot model (.keras, .onnx, .pt)
- `dataset/`, `training/`, `notebooks/`, `evaluation/` - Riset & pelatihan

## Menjalankan (dev)
```bash
cd ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn service.main:app --host 0.0.0.0 --port 8001
```

Model MVP disimpan di `ai/weights/agronia_rice_mobilenetv2.keras` dan tidak
di-commit. Salin hasil training ke lokasi tersebut, lalu isi `AI_MODEL_PATH`
di `ai/.env` (contoh ada di `ai/.env.example`). Registry kelas ada di
`ai/classes.json`.

Python 3.14 belum didukung TensorFlow, sehingga service memakai Keras dengan
backend PyTorch (`KERAS_BACKEND=torch`, sudah diatur di `service/main.py`).
`requirements.txt` mengarahkan pip ke wheel PyTorch CPU.

## Training
Notebook `notebooks/train_rice_colab.ipynb` menjalankan training MobileNetV2
untuk empat kelas padi dan menghasilkan bundle model, `classes.json`, metrik,
serta `splits.csv`. Dataset tidak disertakan di repo.

## Integrasi dengan Backend
Backend Django memanggil `http://localhost:8001/predict` dengan field `file`.
Konfigurasi alamat dan timeout ada di `backend/.env` (`AI_SERVICE_URL`,
`AI_SERVICE_TIMEOUT`).

Backend memetakan kegagalan menjadi:
- `service_unavailable` (503) bila service tidak dapat dijangkau.
- `model_unavailable` (503) bila model belum tersedia.
- `inference_failed` (502) bila respons tidak valid atau kelas tidak terdaftar.
