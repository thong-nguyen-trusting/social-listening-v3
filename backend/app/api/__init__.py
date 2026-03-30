from app.api.browser import router as browser_router
from app.api.health import router as health_router
from app.api.plans import router as plans_router

__all__ = ["browser_router", "health_router", "plans_router"]
