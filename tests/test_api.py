import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def build_payload() -> dict[str, int | float]:
    """Return a representative payload for single prediction tests."""

    return {
        "ID": 1001,
        "LIMIT_BAL": 200000,
        "SEX": 1,
        "EDUCATION": 2,
        "MARRIAGE": 1,
        "AGE": 35,
        "PAY_0": 0,
        "PAY_2": 0,
        "PAY_3": 0,
        "PAY_4": 0,
        "PAY_5": 0,
        "PAY_6": 0,
        "BILL_AMT1": 150000,
        "BILL_AMT2": 140000,
        "BILL_AMT3": 130000,
        "BILL_AMT4": 120000,
        "BILL_AMT5": 110000,
        "BILL_AMT6": 100000,
        "PAY_AMT1": 50000,
        "PAY_AMT2": 40000,
        "PAY_AMT3": 30000,
        "PAY_AMT4": 20000,
        "PAY_AMT5": 10000,
        "PAY_AMT6": 5000,
    }


def test_single_prediction_happy_path() -> None:
    """Ensure the single prediction endpoint returns a probability."""

    response = client.post("/api/v1/predictions", json=build_payload())
    assert response.status_code == 200
    payload = response.json()
    print("single_prediction_response:", payload)
    assert set(payload) == {"id", "probability", "is_default", "threshold"}
    assert payload["id"] == "1001"
    assert 0.0 <= payload["probability"] <= 1.0
    assert isinstance(payload["is_default"], bool)
    assert isinstance(payload["threshold"], float)


def test_batch_prediction_happy_path() -> None:
    """Ensure the batch prediction endpoint responds with a CSV file."""

    rows = [
        build_payload(),
        {**build_payload(), "ID": 1002, "PAY_0": 5},
    ]
    headers = list(rows[0].keys())
    csv_lines = [",".join(headers)]
    for row in rows:
        csv_lines.append(",".join(str(row[col]) for col in headers))
    csv_bytes = "\n".join(csv_lines).encode("utf-8")
    file = {"file": ("batch.csv", io.BytesIO(csv_bytes), "text/csv")}

    response = client.post("/api/v1/predictions/batch", files=file)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    body = response.content.decode("utf-8")
    print("batch_prediction_response:\n", body)
    assert "probability" in body
    assert "is_default" in body
    assert "id" in body
