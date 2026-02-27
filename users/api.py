from ninja import NinjaAPI
from .routers.userRouter import router as user_router
from .routers.adminRouter import router as admin_router

app = NinjaAPI(urls_namespace="user-api")

app.add_router("/users/", user_router)   
app.add_router("/admins/", admin_router)   
