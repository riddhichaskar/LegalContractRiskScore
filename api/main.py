from fastapi import FastAPI
from api.routes.predict import router as predict_router

app = FastAPI(title="Legal Contract Risk Analyzer")

app.include_router(predict_router)

@app.get("/")
def home():
    return {"message": "API is running"}