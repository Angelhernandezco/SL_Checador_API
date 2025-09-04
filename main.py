from fastapi import FastAPI
from api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings

if settings.PRODUCTION:
    app = FastAPI(title="SL API", docs_url=None, redoc_url=None, openapi_url=None)
else:
    app = FastAPI(title="SL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"working": True}
