from fastapi import FastAPI
from src.api.routes import stats
from src.api.routes import ingest, detect, timeline, search, report
from src.api.routes import export
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import predict

app = FastAPI(title="AI Log Forensics System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(export.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(detect.router, prefix="/api")
app.include_router(timeline.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(stats.router, prefix="/api")