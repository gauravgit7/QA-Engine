import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from database.connection import init_db, SessionLocal
from database.models import User
from services.auth_service import hash_password
from utils.exceptions import AppException, app_exception_handler, generic_exception_handler

# Route imports
from routes.auth import router as auth_router
from routes.generate import router as generate_router
from routes.jira import router as jira_router
from routes.config_routes import router as config_router
from routes.history import router as history_router
from routes.dashboard import router as dashboard_router
from routes.user import router as user_router

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("firstfintech")


# ──────────────────────────────────────────────
# Lifespan (startup / shutdown)
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting FirstFintech QA Engine Backend...")

    # Create database tables
    init_db()
    logger.info("Database tables created / verified.")

    # Seed default admin user
    _seed_admin_user()

    yield

    logger.info("Shutting down FirstFintech QA Engine Backend.")


def _seed_admin_user():
    """Create a default admin user if none exists."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@firstfintech.com").first()
        if not existing:
            admin = User(
                username="Gaurav Subedi",
                email="admin@firstfintech.com",
                password_hash=hash_password("admin123"),
            )
            db.add(admin)
            db.commit()
            logger.info("Default admin user created: admin@firstfintech.com / admin123")
        else:
            logger.info("Admin user already exists. Skipping seed.")
    finally:
        db.close()


# ──────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────
app = FastAPI(
    title="FirstFintech QA Engine",
    description="AI-powered test case generation platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ──────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "null",  # Allow file:// origins during local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Exception Handlers
# ──────────────────────────────────────────────
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ──────────────────────────────────────────────
# Register Routers
# ──────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(generate_router)
app.include_router(jira_router)
app.include_router(config_router)
app.include_router(history_router)
app.include_router(dashboard_router)
app.include_router(user_router)


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "success": True,
        "message": "FirstFintech QA Engine API is running.",
        "version": "1.0.0",
    }


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    import sys
    # Allow disabling reload via --no-reload or if not specified
    is_reload = "--reload" in sys.argv
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=is_reload)
