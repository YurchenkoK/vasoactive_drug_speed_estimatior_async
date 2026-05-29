# Vasoactive Drug Speed Estimator — Async Backend

> Course project: Internet Application Development (5th semester), BMSTU

An extended version of the vasoactive drug speed estimator backend, rebuilt with asynchronous task processing and a Tauri-based desktop interface layer.

## Tech Stack

- Python, Django, Django REST Framework
- Redis (async task queue)
- Tauri (cross-platform desktop wrapper)
- Swagger / OpenAPI

## Key Additions over the Base Version

- Redis integration for async background task handling
- Tauri desktop application configuration
- Extended lab coverage through lab 6

## Related Repositories

| Repository | Description |
|---|---|
| [vasoactive_drug_speed_estimatior](https://github.com/YurchenkoK/vasoactive_drug_speed_estimatior) | Original Django backend |
| [vasoactive_drug_speed_estimatior_async](https://github.com/YurchenkoK/vasoactive_drug_speed_estimatior_async) | Async version with Redis (this repo) |
| [vasoactive_drug_speed_estimatior_frontend](https://github.com/YurchenkoK/vasoactive_drug_speed_estimatior_frontend) | React frontend |

## Getting Started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API documentation available at `http://localhost:8000/swagger/`
