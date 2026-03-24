from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from app.database import get_db
from app.models import Base, Aluno, Personal
from app.utils.auth import get_personal_atual
from app.schemas.financeiro import PagamentoCriar, MensalidadeGerar

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

class Pagamento(Base):
    __tablename__ = "pagamentos"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    personal_id = Column(Integer, ForeignKey("personals.id"), nullable=False)
    valor = Column(Float, nullable=False)
    descricao = Column(String(255))
    data_vencimento = Column(Date)
    data_pagamento = Column(Date)
    status = Column(String(20), default="pendente")
    metodo_pagamento = Column(String(50))
    criado_em = Column(DateTime, default=datetime.utcnow)

def get_aluno(aluno_id, personal_id, db):
    a = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal_id).first()
    if not a: raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return a

def cs(p):
    if p.status == "pago": return "pago"
    if p.data_vencimento and p.data_vencimento < date.today(): return "atrasado"
    return "pendente"

def ca(p):
    if p.status != "pago" and p.data_vencimento:
        return max((date.today() - p.data_vencimento).days, 0)
    return 0

@router.post("/pagamento", status_code=201)
def criar(dados: PagamentoCriar, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    get_aluno(dados.aluno_id, personal.id, db)
    p = Pagamento(**dados.model_dump(), personal_id=personal.id)
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id, "valor": p.valor, "descricao": p.descricao, "vencimento": str(p.data_vencimento), "status": cs(p)}

@router.post("/mensalidade/gerar")
def gerar(dados: MensalidadeGerar, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    aluno = get_aluno(dados.aluno_id, personal.id, db)
    hoje = date.today(); criados = []
    for i in range(dados.meses):
        mes = hoje.month + i
        ano = hoje.year + (mes - 1) // 12
        mes = ((mes - 1) % 12) + 1
        try: venc = date(ano, mes, dados.dia_vencimento)
        except ValueError:
            import calendar
            venc = date(ano, mes, calendar.monthrange(ano, mes)[1])
        p = Pagamento(aluno_id=dados.aluno_id, personal_id=personal.id, valor=dados.valor,
            descricao=f"{dados.descricao} - {venc.month:02d}/{venc.year}",
            data_vencimento=venc, status="pendente")
        db.add(p)
        criados.append({"mes": f"{venc.month:02d}/{venc.year}", "vencimento": str(venc), "valor": dados.valor})
    db.commit()
    return {"mensagem": f"{dados.meses} mensalidades geradas para {aluno.nome}", "pagamentos": criados}

@router.get("/pagamento/aluno/{aluno_id}")
def listar(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    get_aluno(aluno_id, personal.id, db)
    ps = db.query(Pagamento).filter(Pagamento.aluno_id == aluno_id).order_by(Pagamento.data_vencimento.desc()).all()
    r = [{"id": p.id, "descricao": p.descricao, "valor": p.valor, "vencimento": str(p.data_vencimento),
          "pagamento": str(p.data_pagamento) if p.data_pagamento else None, "status": cs(p), "dias_atraso": ca(p)} for p in ps]
    return {"resumo": {"pago": round(sum(x["valor"] for x in r if x["status"] == "pago"), 2),
                       "pendente": round(sum(x["valor"] for x in r if x["status"] == "pendente"), 2),
                       "atrasado": round(sum(x["valor"] for x in r if x["status"] == "atrasado"), 2)}, "pagamentos": r}

@router.put("/pagamento/{pid}/pagar")
def pagar(pid: int, metodo: str = Query("pix"), personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    p = db.query(Pagamento).filter(Pagamento.id == pid, Pagamento.personal_id == personal.id).first()
    if not p: raise HTTPException(status_code=404, detail="Pagamento nao encontrado")
    p.status = "pago"; p.data_pagamento = date.today(); p.metodo_pagamento = metodo; db.commit()
    return {"mensagem": "Pagamento registrado!", "valor": p.valor, "data": str(p.data_pagamento), "metodo": metodo}

@router.get("/resumo")
def resumo(personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    hoje = date.today(); mi = date(hoje.year, hoje.month, 1)
    todos = db.query(Pagamento).filter(Pagamento.personal_id == personal.id).all()
    ma = [p for p in todos if p.data_vencimento and p.data_vencimento >= mi]
    rm = sum(p.valor for p in ma if p.status == "pago")
    em = sum(p.valor for p in ma)
    alunos = db.query(Aluno).filter(Aluno.personal_id == personal.id, Aluno.ativo == True).all()
    inad = []
    for a in alunos:
        at = [p for p in todos if p.aluno_id == a.id and cs(p) == "atrasado"]
        if at: inad.append({"aluno": a.nome, "valor": round(sum(p.valor for p in at), 2), "parcelas": len(at)})
    return {"geral": {"recebido": round(sum(p.valor for p in todos if p.status == "pago"), 2),
                      "pendente": round(sum(p.valor for p in todos if cs(p) == "pendente"), 2),
                      "atrasado": round(sum(p.valor for p in todos if cs(p) == "atrasado"), 2)},
            "mes_atual": {"recebido": round(rm, 2), "esperado": round(em, 2),
                          "percentual": round(rm / em * 100, 1) if em > 0 else 0},
            "inadimplentes": inad}