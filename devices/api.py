from ninja import NinjaAPI
from .routers.deviceRouter import router as device_router

app = NinjaAPI(urls_namespace="device-api")

app.add_router("/devices/", device_router)