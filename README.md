# default-credit-card-clients
Predicts credit-card default risk with a FastAPI backend and Streamlit UI.

## Generate the model notebook
1. `pip install -r requirements.txt`
2. Open `notebooks/eda_and_training.ipynb`, run all cells, to export the model artifacts to `models/`.

## Run with uvicorn + Streamlit
```bash
uvicorn app.main:app --reload
streamlit run streamlit_app/streamlit_app.py
```

## Run with Docker
```bash
docker build -t default-credit:latest .
docker run --rm -it -p 8000:8000 default-credit:latest
streamlit run streamlit_app/streamlit_app.py
```

## Test the routes
```bash
pytest -v
```
