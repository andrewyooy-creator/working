from fastapi import FastAPI
from contextlib import asynccontextmanager
from warehous.frd.database.database import engine,Base
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Warehouse Management API", version="1.0.0",lifespan=lifespan)