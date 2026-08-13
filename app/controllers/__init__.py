"""Controller adapters that expose router objects for the FastAPI app.

This module re-exports router modules from the existing `app.routers` package
so the application can import `app.controllers` while preserving current
router implementation and behaviour. Later, business logic can be moved into
`app.services` and DB access into `app.repositories` without changing the
application entry points.
"""
from app.routers import products_api as products_api
from app.routers import users_api as users_api
from app.routers import categories_api as categories_api
from app.routers import reviews_api as reviews_api
from app.routers import notifications_api as notifications_api
from app.routers import orders_api as orders_api
from app.routers import authentication as authentication
from app.routers import chatbot_api as chatbot_api
from app.routers import admins_api as admins_api
from app.routers import sales_api as sales_api
from app.routers import reports_api as reports_api

__all__ = [
    "products_api",
    "users_api",
    "categories_api",
    "reviews_api",
    "notifications_api",
    "orders_api",
    "authentication",
    "chatbot_api",
    "admins_api",
    "sales_api",
    "reports_api",
]
