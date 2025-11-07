FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY credit_default_model ./credit_default_model
COPY models ./models

ENV MODEL_DIR=/app/models \
    MODEL_FILENAME=cat_model_v1.0.0.pkl \
    MODEL_SIGNATURE=cat_model_v1.0.0_input_signature.json \
    MODEL_METADATA=cat_model_v1.0.0_metadata.json

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
