from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SinglePredictionDTO(BaseModel):
    """Data transfer object describing a single applicant."""

    model_config = ConfigDict(extra="ignore")

    ID: Optional[int] = Field(default=1, description="Unique identifier for the applicant.")
    LIMIT_BAL: float = Field(..., description="Credit limit for the client.")
    SEX: int = Field(..., description="Gender indicator of the client.")
    EDUCATION: int = Field(..., description="Education level of the client.")
    MARRIAGE: int = Field(..., description="Marital status of the client.")
    AGE: int = Field(..., description="Age of the client.")
    PAY_0: int = Field(..., description="Repayment status in September.")
    PAY_2: int = Field(..., description="Repayment status in August.")
    PAY_3: int = Field(..., description="Repayment status in July.")
    PAY_4: int = Field(..., description="Repayment status in June.")
    PAY_5: int = Field(..., description="Repayment status in May.")
    PAY_6: int = Field(..., description="Repayment status in April.")
    BILL_AMT1: float = Field(..., description="Bill statement amount in September.")
    BILL_AMT2: float = Field(..., description="Bill statement amount in August.")
    BILL_AMT3: float = Field(..., description="Bill statement amount in July.")
    BILL_AMT4: float = Field(..., description="Bill statement amount in June.")
    BILL_AMT5: float = Field(..., description="Bill statement amount in May.")
    BILL_AMT6: float = Field(..., description="Bill statement amount in April.")
    PAY_AMT1: float = Field(..., description="Amount paid in September.")
    PAY_AMT2: float = Field(..., description="Amount paid in August.")
    PAY_AMT3: float = Field(..., description="Amount paid in July.")
    PAY_AMT4: float = Field(..., description="Amount paid in June.")
    PAY_AMT5: float = Field(..., description="Amount paid in May.")
    PAY_AMT6: float = Field(..., description="Amount paid in April.")


class PredictionResponseDTO(BaseModel):
    """Data transfer object describing a prediction outcome."""

    id: str | None = Field(
        None, description="Identifier of the scored applicant when provided."
    )
    probability: float = Field(..., description="Model probability of default.")
    is_default: bool = Field(
        ..., description="Predicted default flag using configured threshold."
    )
    threshold: float = Field(
        ..., description="Threshold applied to derive the default flag."
    )

