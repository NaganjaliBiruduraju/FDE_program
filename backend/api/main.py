from fastapi import FastAPI

from backend.api.routes import router


app = FastAPI(
    title="FDE Document Extraction API",
    description="API for extracting structured information from PDF documents.",
    version="1.0.0",
)

app.include_router(
    router,
    prefix="/api",
)