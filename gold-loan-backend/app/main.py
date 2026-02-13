from fastapi import FastAPI

from app.api import auth, appraisers, customers, loans, compliance, purity, images, summary, audit, system
from app.config.logging_config import setup_logging
from app.config.settings import settings
from app.core.database import Base, engine
from app.core.exceptions import http_exception_handler
from app.core.middleware import register_middleware


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.app_name, version='v1')
    register_middleware(app)
    app.add_exception_handler(Exception, http_exception_handler)

    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(appraisers.router, prefix=settings.api_prefix)
    app.include_router(customers.router, prefix=settings.api_prefix)
    app.include_router(loans.router, prefix=settings.api_prefix)
    app.include_router(compliance.router, prefix=settings.api_prefix)
    app.include_router(purity.router, prefix=settings.api_prefix)
    app.include_router(images.router, prefix=settings.api_prefix)
    app.include_router(summary.router, prefix=settings.api_prefix)
    app.include_router(audit.router, prefix=settings.api_prefix)
    app.include_router(system.router, prefix=settings.api_prefix)

    Base.metadata.create_all(bind=engine)
    return app


app = create_app()
