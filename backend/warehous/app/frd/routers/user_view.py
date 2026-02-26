from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from warehous.app.entities.models.base.base import Base
from backend.warehous.app.main import oauth2_scheme
from warehous.app.frd.database.database import engine, get_db
from warehous.app.entities.models.user.user_crud import get_user_by_username, create_user, verify_password, hash_password
from warehous.app.entities.models.user.user_schema import UserCreate, UserPublic, Token
from warehous.app.frd.authentication.auth import create_access_token,jwt,JWTError
from backend.warehous.app.main import create_tables
from warehous.app.frd.authentication.auth import SECRET_KEY,ALGORITHM
router = APIRouter()


@router.on_event("startup")
async def startup():
    await create_tables()

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserPublic:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = await get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return UserPublic.from_orm(user)

@router.post("/register", status_code=201, response_model=dict)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")
    hashed = hash_password(body.password)
    await create_user(db, body.username, hashed, body.full_name or "")
    return {"message": "User registered successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserPublic)
async def me(current_user: UserPublic = Depends(get_current_user)):
    return current_user
