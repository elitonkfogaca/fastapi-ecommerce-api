from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.products.router import router as products_router
from app.categories.router import router as categories_router
from app.orders.router import router as orders_router
from app.users.router import router as users_router
from app.core.config import settings
from app.database.session import get_db

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(orders_router)
app.include_router(users_router)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Caso use outro porto
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc
    allow_headers=["*"],  # Permite todos os headers incluindo Authorization
)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "message": str(e)}
