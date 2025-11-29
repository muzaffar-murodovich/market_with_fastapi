from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from starlette import status
from models import User
from schemas import SignUpModel, LoginModel
from database import session, engine
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

auth_router = APIRouter(
    prefix="/auth",
)

session = session(bind=engine)

@auth_router.get("/")
async def welcome(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {
        "message": "Welcome to the Sign Up Page",
        }

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail='User with this email already exists')

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail='User with this username already exists')

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    session.add(new_user)
    session.commit()
    data = {
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email,
        'is_staff': new_user.is_staff,
        'is_active': new_user.is_active
    }
    response_model = {
        'success': True,
        'code': 201,
        'message': "user is created successfully",
        'data': data
    }

    return response_model

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: LoginModel, Authorize: AuthJWT=Depends()):

    db_user = session.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email)
    ).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_lifetime = timedelta(minutes=30)
        refresh_lifetime = timedelta(days=3)
        access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)

        token = {
            "access": access_token,
            "refresh": refresh_token ,
        }

        response = {
            'success': True,
            'code': 201,
            'message': "login successfully",
            'data': token
        }

        return response
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@auth_router.get("/login/refresh")
async def login_refresh(Authorize: AuthJWT = Depends()):

    try:
        access_lifetime = timedelta(minutes=30)
        refresh_lifetime = timedelta(days=3)
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()

        db_user = session.query(User).filter(User.username == current_user).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        new_access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        response_model = {
            'success': True,
            'code': 201,
            'message': "New access token created successfully",
            'data': {
                'access_token': new_access_token
            }
        }
        return response_model

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")