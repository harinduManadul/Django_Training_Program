from ninja import Router
from django.contrib.auth.hashers import check_password
from users.auth import JWTAuth, create_access_token, roles_allowed
from ..schemas import AuthSchema, ErrorSchema, LoginSchema, UserSchema, TokenSchema
from ..models import User
from typing import Optional

router = Router()

@router.post(
    "/login",
    response={200: TokenSchema, 401: ErrorSchema},
)
def login(request, data: LoginSchema):
    user: Optional[User] = User.objects.filter(username=data.username).first()
    if user is None:
        return 401, {"error": "Invalid username or password"}
    if not check_password(data.password, user.password):
        return 401, {"error": "Invalid username or password"}
    token = create_access_token({
        "username": user.username,
        "user_id": user.pk,
        "role": user.role
        })
    return 200, {"access_token": token,
                  "username": user.username,
                  "role": user.role
                }

@router.get(
    "/authenticate",
    response={200: AuthSchema, 401: ErrorSchema},
    auth = JWTAuth()
)
def authenticate_user(request):
    return request.auth
