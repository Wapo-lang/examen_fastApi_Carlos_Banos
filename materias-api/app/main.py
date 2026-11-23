# app/main.py - agrega el import y el include_router
from fastapi import FastAPI

from app.rutas import router  # <- nuevo

app = FastAPI(title="API Cooperativa de Transporte", version="1.0.0")
app.include_router(router)  # <- nuevo


@app.get("/")
def raiz() -> dict:
    return {"api": "rutas", "docs": "/docs"}