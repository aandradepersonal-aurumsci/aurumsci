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


LIMITES_PLANO = {'bronze': 10, 'prata': 20, 'ouro': 50, 'diamante': 999999}

router = APIRouter(prefix="/alunos", tags=["Alunos"])

@router.get("", response_model=PaginacaoAlunos)
def listar(pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100), busca: Optional[str] = None, apenas_ativos: bool = True, objetivo: Optional[str] = None, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return listar_alunos(personal_id=personal.id, db=db, pagina=pagina, por_pagina=por_pagina, busca=busca, apenas_ativos=apenas_ativos, objetivo=objetivo)

@router.get("/stats")
def stats(personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    return estatisticas_alunos(personal.id, db)

@router.post("", response_model=AlunoResposta, status_code=201)
def criar(dados: AlunoCriar, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.models import Aluno as AlunoModel
    total = db.query(AlunoModel).filter(AlunoModel.personal_id == personal.id, AlunoModel.ativo == True).count()
    limite = LIMITES_PLANO.get(personal.plano or 'bronze', 10)
    if total >= limite:
        raise HTTPException(status_code=403, detail=f'Limite de {limite} alunos atingido para o plano {(personal.plano or "bronze").upper()}. Faça upgrade em aurumsc.com.br')
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
    """BUG FIX 04/05/2026: cascade COMPLETO - deleta hierarquia inteira em ordem"""
    from sqlalchemy import text
    
    aluno = buscar_aluno(aluno_id, personal.id, db)
    nome_aluno = aluno.nome
    
    try:
        # 1. Hierarquia treino (mais profundo primeiro)
        # ExercicioSessao -> SessaoTreino -> PlanoTreino
        db.execute(text("""
            DELETE FROM exercicios_sessao 
            WHERE sessao_id IN (
                SELECT s.id FROM sessoes_treino s 
                JOIN planos_treino p ON s.plano_id = p.id 
                WHERE p.aluno_id = :aid
            )
        """), {"aid": aluno_id})
        
        db.execute(text("""
            DELETE FROM sessoes_treino 
            WHERE plano_id IN (
                SELECT id FROM planos_treino WHERE aluno_id = :aid
            )
        """), {"aid": aluno_id})
        
        db.execute(text("DELETE FROM planos_treino WHERE aluno_id = :aid"), {"aid": aluno_id})
        
        # 2. Outras tabelas dependentes
        db.execute(text("DELETE FROM presencas WHERE aluno_id = :aid"), {"aid": aluno_id})
        db.execute(text("DELETE FROM anamneses WHERE aluno_id = :aid"), {"aid": aluno_id})
        db.execute(text("DELETE FROM avaliacoes_fisicas WHERE aluno_id = :aid"), {"aid": aluno_id})
        db.execute(text("DELETE FROM mensagens_chat WHERE aluno_id = :aid"), {"aid": aluno_id})
        db.execute(text("DELETE FROM pagamentos WHERE aluno_id = :aid"), {"aid": aluno_id})
        db.execute(text("DELETE FROM contratos_servico WHERE aluno_id = :aid"), {"aid": aluno_id})
        db.execute(text("DELETE FROM aluno_credenciais WHERE aluno_id = :aid"), {"aid": aluno_id})
        
        # 3. Por ultimo, o aluno
        db.execute(text("DELETE FROM alunos WHERE id = :aid"), {"aid": aluno_id})
        
        db.commit()
        return {"mensagem": f"Aluno {nome_aluno} excluido permanentemente"}
    
    except Exception as e:
        db.rollback()
        print(f"[DELETE ERROR] aluno_id={aluno_id}: {e}")
        raise HTTPException(500, f"Erro ao excluir: {str(e)}")
