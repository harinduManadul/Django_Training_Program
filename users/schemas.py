from ninja import ModelSchema, Schema
from .models import User
from typing import List, Optional
from pydantic import BaseModel

class UserSchema(ModelSchema):
    device_ids: Optional[list[int]] = None
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'role', 'created_at']
    
    @staticmethod
    def resolve_device_ids(obj):
        return list(obj.device_ids.values_list('id', flat=True))
        
class UserCreateSchema(BaseModel):
    name: str
    username: str
    email: str
    password: str
    role: str
    
class LoginSchema(Schema):
    username: str
    password: str
    
class TokenSchema(Schema):
    access_token: str
    username: str
    role: str
    
class AuthSchema(Schema):
    id: int
    name: str
    email: str
    username: str
    role: str    
    
class ErrorSchema(Schema):
    error: str