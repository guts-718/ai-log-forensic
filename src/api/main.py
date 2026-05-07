from fastapi import FastAPI
from src.api.routes import ingest, detect, timeline, search, report

app = FastAPI(title="AI Log Forensics System")
from src.api.routes import predict

app.include_router(predict.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(detect.router, prefix="/api")
app.include_router(timeline.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(report.router, prefix="/api")