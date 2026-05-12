from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from app.database import get_db
from app.models import Base, Aluno, Personal
from app.utils.auth import get_personal_atual
from app.schemas.avaliacao import AvaliacaoCriar, AvaliacaoResposta

router = APIRouter(prefix="/avaliacao", tags=["Avaliacao Fisica"])

class AvaliacaoFisica(Base):
    __tablename__ = "avaliacoes_fisicas"
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    data_avaliacao = Column(Date, default=date.today)
    peso = Column(Float)
    estatura = Column(Float)
    imc = Column(Float)
    classificacao_imc = Column(String(50))
    dc_peitoral = Column(Float)
    dc_abdominal = Column(Float)
    dc_coxa = Column(Float)
    dc_triciptal = Column(Float)
    dc_suprailíaca = Column(Float)
    densidade_corporal = Column(Float)
    percentual_gordura = Column(Float)
    classificacao_gordura = Column(String(50))
    massa_gorda_kg = Column(Float)
    massa_magra_kg = Column(Float)
    circ_pescoco = Column(Float)
    circ_torax = Column(Float)
    circ_cintura = Column(Float)
    circ_abdomen = Column(Float)
    circ_quadril = Column(Float)
    circ_braco_d_relaxado = Column(Float)
    circ_braco_d_contraido = Column(Float)
    circ_braco_e_relaxado = Column(Float)
    circ_braco_e_contraido = Column(Float)
    circ_antebraco_d = Column(Float)
    circ_antebraco_e = Column(Float)
    circ_coxa_d = Column(Float)
    circ_coxa_e = Column(Float)
    circ_panturrilha_d = Column(Float)
    circ_panturrilha_e = Column(Float)
    relacao_cintura_quadril = Column(Float)
    risco_cardiovascular = Column(String(50))
    teste_flexibilidade_cm = Column(Float)
    classificacao_flexibilidade = Column(String(50))
    teste_flexao_num = Column(Integer)
    classificacao_flexao = Column(String(50))
    teste_barra_num = Column(Integer)
    teste_cooper_metros = Column(Float)
    vo2max = Column(Float)
    classificacao_vo2 = Column(String(50))
    postura_cabeca = Column(String(1000))
    postura_ombros = Column(String(1000))
    postura_coluna = Column(String(1000))
    postura_quadril = Column(String(1000))
    postura_joelhos = Column(String(1000))
    postura_pes = Column(String(1000))
    postura_observacoes = Column(Text)
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

def get_aluno(aluno_id, personal_id, db):
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return aluno

def calcular_idade(data_nasc):
    if not data_nasc:
        return 30
    hoje = date.today()
    return hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))

def calc_imc(peso, estatura_cm):
    if not peso or not estatura_cm:
        return None, None
    imc = peso / (estatura_cm / 100) ** 2
    if imc < 18.5: cls = "Abaixo do peso"
    elif imc < 25: cls = "Peso normal"
    elif imc < 30: cls = "Sobrepeso"
    elif imc < 35: cls = "Obesidade Grau I"
    elif imc < 40: cls = "Obesidade Grau II"
    else: cls = "Obesidade Grau III"
    return round(imc, 2), cls

def pollock_m(p, a, c, idade):
    if not all([p, a, c, idade]): return None, None, None
    soma = p + a + c
    d = 1.10938 - (0.0008267*soma) + (0.0000016*soma**2) - (0.0002574*idade)
    pct = ((4.95/d) - 4.50) * 100
    cls = "Atleta" if pct < 14 else ("Boa forma" if pct < 18 else ("Aceitavel" if pct < 25 else "Obesidade"))
    return round(d,4), round(pct,2), cls

def pollock_f(t, s, c, idade):
    if not all([t, s, c, idade]): return None, None, None
    soma = t + s + c
    d = 1.0994921 - (0.0009929*soma) + (0.0000023*soma**2) - (0.0001392*idade)
    pct = ((4.95/d) - 4.50) * 100
    cls = "Atleta" if pct < 21 else ("Boa forma" if pct < 25 else ("Aceitavel" if pct < 32 else "Obesidade"))
    return round(d,4), round(pct,2), cls

def calc_rcq(cintura, quadril, sexo):
    if not cintura or not quadril: return None, None
    rcq = cintura / quadril
    if sexo == "masculino": risco = "Baixo" if rcq < 0.90 else ("Moderado" if rcq <= 0.95 else "Alto")
    else: risco = "Baixo" if rcq < 0.80 else ("Moderado" if rcq <= 0.85 else "Alto")
    return round(rcq,3), risco

def calc_cooper(dist):
    if not dist: return None, None
    vo2 = max((dist - 504.9) / 44.73, 0)
    cls = "Superior" if vo2 >= 56 else ("Excelente" if vo2 >= 51 else ("Bom" if vo2 >= 43 else ("Regular" if vo2 >= 34 else "Fraco")))
    return round(vo2,2), cls

def calc_wells(dist, sexo):
    if dist is None: return None
    t = {"masculino":[(40,"Excelente"),(34,"Acima da media"),(27,"Media"),(17,"Abaixo da media"),(0,"Fraco")], "feminino":[(41,"Excelente"),(38,"Acima da media"),(33,"Media"),(25,"Abaixo da media"),(0,"Fraco")]}
    for m, c in t.get(sexo, t["masculino"]):
        if dist >= m: return c
    return "Fraco"

def calc_flexao(reps, sexo, idade):
    if reps is None: return None
    nm = [(20,29,36),(30,39,30),(40,49,25),(50,59,21),(60,99,18)]
    nf = [(20,29,30),(30,39,27),(40,49,24),(50,59,21),(60,99,17)]
    normas = nm if sexo == "masculino" else nf
    ref = next((r for i,f,r in normas if i <= idade <= f), 18)
    return "Excelente" if reps >= ref else ("Bom" if reps >= ref*0.8 else ("Regular" if reps >= ref*0.6 else "Fraco"))

@router.post("", response_model=AvaliacaoResposta, status_code=201)
def criar(dados: AvaliacaoCriar, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    aluno = get_aluno(dados.aluno_id, personal.id, db)
    idade = calcular_idade(aluno.data_nascimento)
    sexo = aluno.sexo.value if aluno.sexo else "masculino"
    av = AvaliacaoFisica(**dados.model_dump())
    av.imc, av.classificacao_imc = calc_imc(dados.peso, dados.estatura)
    if sexo == "masculino":
        av.densidade_corporal, av.percentual_gordura, av.classificacao_gordura = pollock_m(dados.dc_peitoral, dados.dc_abdominal, dados.dc_coxa, idade)
    else:
        av.densidade_corporal, av.percentual_gordura, av.classificacao_gordura = pollock_f(dados.dc_triciptal, dados.dc_suprailíaca, dados.dc_coxa, idade)
    if av.percentual_gordura and dados.peso:
        av.massa_gorda_kg = round(dados.peso * (av.percentual_gordura/100), 2)
        av.massa_magra_kg = round(dados.peso - av.massa_gorda_kg, 2)
    av.relacao_cintura_quadril, av.risco_cardiovascular = calc_rcq(dados.circ_cintura, dados.circ_quadril, sexo)
    av.vo2max, av.classificacao_vo2 = calc_cooper(dados.teste_cooper_metros)
    av.classificacao_flexibilidade = calc_wells(dados.teste_flexibilidade_cm, sexo)
    av.classificacao_flexao = calc_flexao(dados.teste_flexao_num, sexo, idade)
    db.add(av)
    db.commit()
    db.refresh(av)
    return av

@router.get("/aluno/{aluno_id}")
def historico(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    get_aluno(aluno_id, personal.id, db)
    return db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno_id).order_by(AvaliacaoFisica.data_avaliacao.desc()).all()

@router.get("/{avaliacao_id}", response_model=AvaliacaoResposta)
def detalhe(avaliacao_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    av = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.id == avaliacao_id).first()
    if not av: raise HTTPException(status_code=404, detail="Avaliacao nao encontrada")
    get_aluno(av.aluno_id, personal.id, db)
    return av

@router.get("/{avaliacao_id}/relatorio")
def relatorio(avaliacao_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    av = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.id == avaliacao_id).first()
    if not av: raise HTTPException(status_code=404, detail="Avaliacao nao encontrada")
    aluno = get_aluno(av.aluno_id, personal.id, db)
    return {"aluno": aluno.nome, "data": str(av.data_avaliacao), "composicao_corporal": {"peso_kg": av.peso, "estatura_cm": av.estatura, "imc": av.imc, "classificacao_imc": av.classificacao_imc, "percentual_gordura": av.percentual_gordura, "classificacao_gordura": av.classificacao_gordura, "massa_gorda_kg": av.massa_gorda_kg, "massa_magra_kg": av.massa_magra_kg}, "circunferencias": {"cintura_cm": av.circ_cintura, "quadril_cm": av.circ_quadril, "rcq": av.relacao_cintura_quadril, "risco_cardiovascular": av.risco_cardiovascular}, "testes_fisicos": {"flexibilidade_cm": av.teste_flexibilidade_cm, "classificacao_flexibilidade": av.classificacao_flexibilidade, "flexao_repeticoes": av.teste_flexao_num, "classificacao_flexao": av.classificacao_flexao, "barra_repeticoes": av.teste_barra_num, "cooper_metros": av.teste_cooper_metros, "vo2max": av.vo2max, "classificacao_vo2": av.classificacao_vo2}, "postura": {"cabeca": av.postura_cabeca, "ombros": av.postura_ombros, "coluna": av.postura_coluna}, "observacoes": av.observacoes}

@router.delete("/{avaliacao_id}")
def deletar(avaliacao_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    av = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.id == avaliacao_id).first()
    if not av: raise HTTPException(status_code=404, detail="Avaliacao nao encontrada")
    get_aluno(av.aluno_id, personal.id, db)
    db.delete(av)
    db.commit()
    return {"mensagem": "Avaliacao removida com sucesso"}
