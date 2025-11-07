import os
import json
import io
import httpx
import pandas as pd
import streamlit as st

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


@st.cache_data(show_spinner=False)
def read_csv_preview(file_bytes: bytes, n_rows: int = 5) -> pd.DataFrame:
    """Return a small preview of the uploaded CSV."""

    buffer = io.BytesIO(file_bytes)
    return pd.read_csv(buffer).head(n_rows)


def post_single_prediction(payload: dict) -> dict:
    """Send the single prediction request to the API."""

    url = f"{API_BASE_URL}/api/v1/predictions"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


def post_batch_prediction(file: bytes, filename: str) -> str:
    """Send the batch prediction request and return CSV text."""

    url = f"{API_BASE_URL}/api/v1/predictions/batch"
    files = {"file": (filename, file, "text/csv")}
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, files=files)
        response.raise_for_status()
        return response.text


st.set_page_config(page_title="Default Client Predictions", layout="wide")
st.title("Default Credit Risk — Demo Console")

tabs = st.tabs(["Single Prediction", "Batch Prediction"])

with tabs[0]:
    st.subheader("Single Prediction")
    default_payload = {
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

    st.caption("Paste or edit the JSON request body below.")
    raw_json = st.text_area(
        "Request JSON",
        value=json.dumps(default_payload, indent=2),
        height=400,
        label_visibility="collapsed",
    )

    single_history = st.session_state.setdefault("single_history", [])
    if st.button("Send Single Prediction", width='stretch'):
        try:
            payload = json.loads(raw_json)
            result = post_single_prediction(payload)
            single_history.insert(0, result)
            st.success("Prediction completed.")
        except json.JSONDecodeError as err:
            st.error(f"Invalid JSON payload: {err}")
        except httpx.HTTPError as err:
            st.error(f"API request failed: {err}")

    if single_history:
        st.markdown("### Recent Responses")
        for idx, item in enumerate(single_history[:5], start=1):
            with st.expander(f"Response #{idx}", expanded=(idx == 1)):
                st.json(item)

with tabs[1]:
    st.subheader("Batch Prediction")
    st.caption("Upload a CSV file containing the batch of clients to score.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()

        with st.expander("CSV Preview", expanded=False):
            try:
                preview_df = read_csv_preview(file_bytes)
                st.dataframe(preview_df, width='stretch')
            except Exception as err:
                st.warning(f"Unable to preview CSV: {err}")

        if st.button("Run Batch Prediction", width='stretch'):
            try:
                csv_text = post_batch_prediction(file_bytes, uploaded_file.name)
                st.success("Batch prediction completed.")
                st.download_button(
                    "Download Results",
                    data=csv_text.encode("utf-8"),
                    file_name="batch_predictions.csv",
                    mime="text/csv",
                    width='stretch',
                )
                st.markdown("#### Sample Output")
                st.code(csv_text.splitlines()[:10], language="text")
            except httpx.HTTPError as err:
                st.error(f"API request failed: {err}")
