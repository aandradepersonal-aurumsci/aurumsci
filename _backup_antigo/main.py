"""
AurumSci — Ponto de entrada FastAPI
Motor v1 integrado
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
import os

from app.config import settings
from app.database import engine
from app.models import Base

from app.routers import auth, alunos, anamnese, avaliacao
from app.routers.treino import router as treino_router
from app.routers.financeiro import router as financeiro_router
from app.routers.portal_aluno import router as portal_aluno_router
from app.routers.admin import router as admin_router
from app.routers.chatbot import router as chatbot_router
from app.routers.postural_ia import router as postural_ia_router
from app.routers.app_aluno import router as app_aluno_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AurumSci",
    description="Plataforma premium para personal trainers — Motor v1",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(alunos.router)
app.include_router(anamnese.router)
app.include_router(avaliacao.router)
app.include_router(treino_router)
app.include_router(financeiro_router)
app.include_router(portal_aluno_router)
app.include_router(admin_router)
app.include_router(chatbot_router)
app.include_router(postural_ia_router)
app.include_router(app_aluno_router)

@app.get("/", tags=["Status"])
def root():
    return {"app": "AurumSci", "versao": "1.0.0", "motor": "v1", "status": "online", "docs": "/docs"}

@app.get("/health", tags=["Status"])
def health():
    return {"status": "ok"}
