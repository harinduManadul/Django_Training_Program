from datetime import timedelta
from functools import wraps
from jose import jwt, JWTError
from django.conf import settings
from django.utils import timezone
from ninja.security import HttpBearer
from .models import User
from ninja.errors import HttpError

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = timezone.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
    "exp": expire,
    "type": "access"
})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            username = payload.get("username")
            user = User.objects.filter(username=username).first()

            if not user:
                return None

            return user

        except JWTError:
            return None
        

def roles_allowed(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.auth.role not in allowed_roles:
                raise HttpError(403, "Permission denied")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator