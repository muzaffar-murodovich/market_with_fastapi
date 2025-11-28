from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': "test",
                'email': "sdgdgsdfgdfg",
                'password': "password12345",
                'is_staff': False,
                "is_active": True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str = '202ecf6860285871efcfbfb4c6246206eb06fbd634e9994e3da4b24da1f4aeec'

class LoginModel(BaseModel):
    username_or_email: str
    password: str