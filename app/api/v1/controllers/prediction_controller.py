import io
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from app.domain.dtos.prediction import PredictionResponseDTO, SinglePredictionDTO
from app.services import PredictionError, PredictionService, get_prediction_service

router = APIRouter(prefix="/predictions")
LOGGER = logging.getLogger(__name__)


@router.post(
    "",
    response_model=PredictionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Score a single applicant",
)
async def predict_single(
    payload: SinglePredictionDTO,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponseDTO:
    """Return default probability for a single payload."""

    try:
        result = await service.predict_single(payload.model_dump())
        return PredictionResponseDTO(**result)
    except PredictionError as exc:
        LOGGER.warning("Single prediction rejected: %s", exc)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Unexpected error during single prediction.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction failed.") from exc


@router.post(
    "/batch",
    status_code=status.HTTP_200_OK,
    summary="Score a batch file",
    response_description="CSV file containing probabilities and default flags.",
)
async def predict_batch(
    file: UploadFile = File(...),
    service: PredictionService = Depends(get_prediction_service),
) -> StreamingResponse:
    """Return probabilities for each row in the uploaded batch file."""

    try:
        content = await file.read()
        dataframe = await service.predict_batch(content, file.filename or "batch.csv")

        buffer = io.StringIO()
        dataframe.to_csv(buffer, index=False)
        buffer.seek(0)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        filename = f"predictions_{timestamp}.csv"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(buffer, media_type="text/csv", headers=headers)
    
    except PredictionError as exc:
        LOGGER.warning("Batch prediction rejected: %s", exc)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Unexpected error during batch prediction.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Batch prediction failed.") from exc
