# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import init_db
from app.utils.logger import get_logger

from app.api import api_router  # ✅ single import, not individual routers

logger = get_logger("main")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        description="AI Tutor Backend API - An intelligent tutoring system powered by LLMs.",
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["https://aitutor.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ✅ Single unified router (avoids duplicate includes)
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    async def on_startup():
        logger.info("🚀 Starting up AI Tutor Backend...")
        try:
            await init_db()
            logger.info("✅ Database initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Error during startup: {e}")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("🛑 Shutting down AI Tutor Backend...")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
