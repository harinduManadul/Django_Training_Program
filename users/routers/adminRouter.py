import token
from typing import Optional
from urllib import response
from django_extensions import settings
from jose import jwt
from ninja import Router
from ..models import User
from ..schemas import UserSchema, ErrorSchema, LoginSchema, UserCreateSchema, TokenSchema, AuthSchema
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from ..auth import JWTAuth, create_access_token, roles_allowed

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


@router.post("/userCreate", response={
    201: UserSchema,
    400: ErrorSchema,
},auth = JWTAuth())
@roles_allowed('admin')
def create_user(request, data: UserCreateSchema):
    
    if User.objects.filter(username=data.username).exists():
        return 400, {"error": "Username already exists"}

    hashed_password = make_password(data.password)
    user = User.objects.create(
        name=data.name,
        username=data.username,
        email=data.email,
        password=hashed_password,
        role=data.role
    )
    return 201, user

@router.get("/all", response=list[UserSchema], auth = JWTAuth())
@roles_allowed('admin')
def list_all_users(request):
    return User.objects.all()  

@router.post("/adminCreate", response={
    201: UserSchema,
    400: ErrorSchema,})
# @roles_allowed('admin')
def create_admin_user(request, data: UserCreateSchema):
    
    if User.objects.filter(username=data.username).exists():
        return 400, {"error": "Username already exists"}

    hashed_password = make_password(data.password)
    user = User.objects.create(
        name=data.name,
        username=data.username,
        email=data.email,
        password=hashed_password,
        role='admin'
    )
    return 201, user