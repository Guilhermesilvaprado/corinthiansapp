import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Resolve bug do asyncio + asyncpg no Windows
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import app.routers.users as users
import app.routers.auth as auth
import app.routers.pessoa as pessoa
from app.routers import superadmin as superadmin_router 
from app.routers import admin_users


app = FastAPI(
    title="App Fiscal API",
    description="Sistema Fiscal Multiempresa",
    version="1.0.0"
)

# CORS - libera seu frontend React/Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas básicas
@app.get("/")
async def root():
    return {"message": "App Fiscal API está rodando! 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# Routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(pessoa.router)
app.include_router(superadmin_router.router)
app.include_router(admin_users.router) 

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)