FROM python:3.11-slim AS api

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY credit_default_model ./credit_default_model
COPY models ./models

ENV MODEL_DIR=/app/models \
    MODEL_FILENAME=rf_model_v0.1.0.pkl \
    MODEL_SIGNATURE=rf_model_v0.1.0_input_signature.json \
    MODEL_METADATA=rf_model_v0.1.0_metadata.json

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
