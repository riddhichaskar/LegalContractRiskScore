from fastapi import APIRouter
from pydantic import BaseModel

from api.services.risk_analyzer import analyze_contract

router = APIRouter()


class ContractRequest(BaseModel):
    text: str


@router.post("/predict")
def predict(request: ContractRequest):
    result = analyze_contract(request.text)
    return {"results": result}