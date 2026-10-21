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
Backend Django akan memanggil `http://localhost:8001/predict` dengan file gambar.
