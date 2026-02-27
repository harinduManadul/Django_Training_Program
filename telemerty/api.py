from ninja import NinjaAPI
from .routers.telemertyRouter import router as telemerty_router

app = NinjaAPI(urls_namespace="telemetry-api")

app.add_router("/telemetry/", telemerty_router)