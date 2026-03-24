from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from app.models import Aluno, ObjetivoAluno, NivelExperiencia
from app.schemas.aluno import AlunoCriar, AlunoAtualizar, AlunoListagem, PaginacaoAlunos

def calcular_idade(data_nascimento):
    if not data_nascimento:
        return None
    hoje = date.today()
    return (hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)))

def criar_aluno(personal_id, dados, db):
    if dados.email:
        if db.query(Aluno).filter(Aluno.email == dados.email, Aluno.personal_id == personal_id).first():
            raise HTTPException(status_code=400, detail="Email ja cadastrado")
    if dados.cpf:
        if db.query(Aluno).filter(Aluno.cpf == dados.cpf).first():
            raise HTTPException(status_code=400, detail="CPF ja cadastrado")
    aluno = Aluno(**dados.model_dump(), personal_id=personal_id)
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno

def listar_alunos(personal_id, db, pagina=1, por_pagina=20, busca=None, apenas_ativos=True, objetivo=None):
    query = db.query(Aluno).filter(Aluno.personal_id == personal_id)
    if apenas_ativos:
        query = query.filter(Aluno.ativo == True)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(or_(Aluno.nome.ilike(termo), Aluno.email.ilike(termo), Aluno.telefone.ilike(termo)))
    if objetivo:
        query = query.filter(Aluno.objetivo == objetivo)
    total = query.count()
    alunos = query.order_by(Aluno.nome).offset((pagina - 1) * por_pagina).limit(por_pagina).all()
    alunos_lista = []
    for a in alunos:
        d = AlunoListagem.model_validate(a)
        d.idade = calcular_idade(a.data_nascimento)
        alunos_lista.append(d)
    return PaginacaoAlunos(total=total, pagina=pagina, por_pagina=por_pagina, alunos=alunos_lista)

def buscar_aluno(aluno_id, personal_id, db):
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return aluno

def atualizar_aluno(aluno_id, personal_id, dados, db):
    aluno = buscar_aluno(aluno_id, personal_id, db)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(aluno, campo, valor)
    db.commit()
    db.refresh(aluno)
    return aluno

def desativar_aluno(aluno_id, personal_id, db):
    aluno = buscar_aluno(aluno_id, personal_id, db)
    aluno.ativo = False
    db.commit()
    return {"mensagem": f"Aluno desativado com sucesso"}

def reativar_aluno(aluno_id, personal_id, db):
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    aluno.ativo = True
    db.commit()
    db.refresh(aluno)
    return aluno

def estatisticas_alunos(personal_id, db):
    total = db.query(func.count(Aluno.id)).filter(Aluno.personal_id == personal_id).scalar()
    ativos = db.query(func.count(Aluno.id)).filter(Aluno.personal_id == personal_id, Aluno.ativo == True).scalar()
    por_objetivo = {}
    for obj in ObjetivoAluno:
        count = db.query(func.count(Aluno.id)).filter(Aluno.personal_id == personal_id, Aluno.objetivo == obj, Aluno.ativo == True).scalar()
        if count:
            por_objetivo[obj.value] = count
    por_nivel = {}
    for nivel in NivelExperiencia:
        count = db.query(func.count(Aluno.id)).filter(Aluno.personal_id == personal_id, Aluno.nivel_experiencia == nivel, Aluno.ativo == True).scalar()
        if count:
            por_nivel[nivel.value] = count
    return {"total_alunos": total, "alunos_ativos": ativos, "alunos_inativos": total - ativos, "por_objetivo": por_objetivo, "por_nivel": por_nivel}
