from contextlib import asynccontextmanager
from warehous.app.frd.database.database import engine,Base
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from warehous.app.frd.routers.category_view import router as category_router
from warehous.app.frd.routers.movement_view import router as movement_router
from warehous.app.frd.routers.product_view import router as product_router
from warehous.app.frd.routers.user_view import router as user_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Warehouse Management API", version="1.0.0",lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(category_router)
app.include_router(movement_router)
app.include_router(product_router)
app.include_router(user_router)