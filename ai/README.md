# Agronia AI Service

Service terpisah untuk inference, training, dan eksperimen AI.

## Struktur
- `service/` - FastAPI service untuk inference
- `inference/` - Logic preprocessing & inference
- `weights/` - File bobot model (.pt, .onnx)
- `dataset/`, `training/`, `notebooks/`, `evaluation/` - Riset & pelatihan

## Menjalankan (dev)
```bash
cd ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn service.main:app --reload --port 8001
```

## Integrasi dengan Backend
Backend Django memanggil `http://localhost:8001/predict` dengan field `file`.
Konfigurasi alamat dan timeout ada di `backend/.env` (`AI_SERVICE_URL`,
`AI_SERVICE_TIMEOUT`).

Backend memetakan kegagalan menjadi:
- `service_unavailable` (503) bila service tidak dapat dijangkau.
- `model_unavailable` (503) bila model belum tersedia.
- `inference_failed` (502) bila respons tidak valid atau kelas tidak terdaftar.
