from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cogniv_vault.api import documents, health, query, ws
from cogniv_vault.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Cogniv-Vault", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(documents.router, prefix="/api/v1")
    app.include_router(query.router, prefix="/api/v1")
    app.include_router(ws.router)

    return app


app = create_app()
