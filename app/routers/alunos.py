from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os  # noqa: F401
from app.database import get_db
from app.models import Personal
from app.schemas.aluno import AlunoCriar, AlunoAtualizar, AlunoResposta, PaginacaoAlunos
from app.services.aluno_service import criar_aluno, listar_alunos, buscar_aluno, atualizar_aluno, desativar_aluno, reativar_aluno, estatisticas_alunos
from app.utils.auth import get_personal_atual
from app.config import settings

router = APIRouter(prefix="/alunos", tags=["Alunos"])

@router.get("", response_model=PaginacaoAlunos)
def listar(pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100), busca: Optional[str] = None, apenas_ativos: bool = True, objetivo: Optional[str] = None, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return listar_alunos(personal_id=personal.id, db=db, pagina=pagina, por_pagina=por_pagina, busca=busca, apenas_ativos=apenas_ativos, objetivo=objetivo)

@router.get("/stats")
def stats(personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return estatisticas_alunos(personal.id, db)

@router.post("", response_model=AlunoResposta, status_code=201)
def criar(dados: AlunoCriar, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    aluno = criar_aluno(personal_id=personal.id, dados=dados, db=db)
    return AlunoResposta.from_orm_com_idade(aluno)

@router.get("/{aluno_id}", response_model=AlunoResposta)
def detalhe(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return AlunoResposta.from_orm_com_idade(buscar_aluno(aluno_id, personal.id, db))

@router.put("/{aluno_id}", response_model=AlunoResposta)
def atualizar(aluno_id: int, dados: AlunoAtualizar, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return AlunoResposta.from_orm_com_idade(atualizar_aluno(aluno_id, personal.id, dados, db))

@router.delete("/{aluno_id}")
def desativar(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return desativar_aluno(aluno_id, personal.id, db)

@router.patch("/{aluno_id}/reativar", response_model=AlunoResposta)
def reativar(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return AlunoResposta.from_orm_com_idade(reativar_aluno(aluno_id, personal.id, db))

@router.post("/{aluno_id}/foto")
async def upload_foto(aluno_id: int, foto: UploadFile = File(...), personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    aluno = buscar_aluno(aluno_id, personal.id, db)
    if foto.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Formato não suportado. Use JPG, PNG ou WebP")
    conteudo = await foto.read()
    if len(conteudo) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE_MB}MB")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext

@router.delete("/{aluno_id}/permanente")
def excluir_permanente(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.routers.portal_aluno import AlunoCredencial
    from app.routers.treino import PresencaTreino
    from app.routers.financeiro import Pagamento
    aluno = buscar_aluno(aluno_id, personal.id, db)
    db.query(AlunoCredencial).filter(AlunoCredencial.aluno_id == aluno_id).delete()
    db.query(PresencaTreino).filter(PresencaTreino.aluno_id == aluno_id).delete()
    db.query(Pagamento).filter(Pagamento.aluno_id == aluno_id).delete()
    db.delete(aluno)
    db.commit()
    return {"mensagem": f"Aluno {aluno.nome} excluído permanentemente"}
