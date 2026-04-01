from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Aluno
from app.routers.portal_aluno import get_aluno_logado

router = APIRouter(prefix="/app-aluno", tags=["App do Aluno"])

class OnboardingSchema(BaseModel):
    objetivo: str
    nivel_experiencia: str
    dias_disponiveis: int
    restricoes_medicas: Optional[str] = None
    historico_lesoes: Optional[str] = None
    peso: Optional[float] = None
    estatura: Optional[float] = None
    idade: Optional[int] = None
    sexo: Optional[str] = None

class BioimpedanciaSchema(BaseModel):
    peso: float
    percentual_gordura: float
    massa_gorda_kg: Optional[float] = None
    massa_magra_kg: Optional[float] = None

class PresencaSchema(BaseModel):
    sessao_id: Optional[int] = None
    duracao_minutos: Optional[int] = None
    observacao: Optional[str] = None

class ChatSchema(BaseModel):
    mensagem: str
    idioma: Optional[str] = "pt"
    historico: Optional[List[dict]] = []

@router.post("/onboarding")
async def onboarding(dados: OnboardingSchema, aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.motor.periodizacao import gerar_periodizacao, periodizacao_to_dict
    from app.routers.treino import PlanoTreino, SessaoTreino
    import json
    periodizacao = gerar_periodizacao(objetivo=dados.objetivo, nivel=dados.nivel_experiencia, dias_semana=dados.dias_disponiveis, semanas_total=12, data_inicio=date.today())
    periodo_dict = periodizacao_to_dict(periodizacao)
    plano_existente = db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno.id, PlanoTreino.ativo == True).first()
    if plano_existente:
        return {"mensagem": "Bem-vindo de volta ao AurumSci, " + aluno.nome.split()[0] + "!", "plano": {"nome": plano_existente.nome, "objetivo": plano_existente.objetivo, "dias_semana": plano_existente.dias_semana, "semanas": plano_existente.semanas_total, "divisao": "ABCDE", "sessoes": []}, "proxima_etapa": "Seu plano ja esta ativo!"}
    plano = PlanoTreino(aluno_id=aluno.id, personal_id=1, nome=f"Plano {dados.objetivo.capitalize()}", objetivo=dados.objetivo, nivel=dados.nivel_experiencia, dias_semana=dados.dias_disponiveis, semanas_total=12, data_inicio=date.today(), ativo=True, periodizacao=json.dumps(periodo_dict, ensure_ascii=False))
    db.add(plano)
    db.flush()
    for i, sessao_nome in enumerate(periodizacao.divisao_sessoes):
        from app.routers.treino import SessaoTreino
        sessao = SessaoTreino(plano_id=plano.id, nome=sessao_nome, dia_semana=i)
        db.add(sessao)
    db.commit()
    return {"mensagem": f"Bem-vindo ao AurumSci, {aluno.nome.split()[0]}!", "plano": {"nome": plano.nome, "objetivo": dados.objetivo, "dias_semana": dados.dias_disponiveis, "semanas": 12, "divisao": periodizacao.divisao_nome, "sessoes": periodizacao.divisao_sessoes}, "proxima_etapa": "Complete sua bioimpedancia e analise postural!"}

@router.post("/bioimpedancia")
async def registrar_bioimpedancia(dados: BioimpedanciaSchema, aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.motor.calculos import bioimpedancia, calcular_massas
    from app.routers.avaliacao import AvaliacaoFisica
    resultado = bioimpedancia(percentual_gordura=dados.percentual_gordura, peso=dados.peso, massa_gorda_kg=dados.massa_gorda_kg, massa_magra_kg=dados.massa_magra_kg)
    resultado = calcular_massas(resultado, dados.peso)
    aval = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno.id).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    if not aval or aval.data_avaliacao != date.today():
        aval = AvaliacaoFisica(aluno_id=aluno.id, personal_id=1, data_avaliacao=date.today(), protocolo_composicao="bioimpedancia")
        db.add(aval)
    aval.peso = dados.peso
    aval.percentual_gordura = resultado.percentual_gordura
    aval.massa_gorda_kg = resultado.massa_gorda_kg
    aval.massa_magra_kg = resultado.massa_magra_kg
    aval.classificacao_gordura = resultado.classificacao_gordura
    db.commit()
    return {"mensagem": "Bioimpedancia registrada!", "composicao": {"peso": dados.peso, "percentual_gordura": resultado.percentual_gordura, "classificacao": resultado.classificacao_gordura, "massa_gorda_kg": resultado.massa_gorda_kg, "massa_magra_kg": resultado.massa_magra_kg}}

@router.post("/postural")
async def analise_postural(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db), foto_frente: Optional[UploadFile] = File(None), foto_lado: Optional[UploadFile] = File(None), foto_costas: Optional[UploadFile] = File(None)):
    import base64
    from app.motor.ia_postural import analisar_postural
    from app.routers.avaliacao import AvaliacaoFisica
    mime_f = foto_frente.content_type if foto_frente else "image/jpeg"
    mime_l = foto_lado.content_type if foto_lado else "image/jpeg"
    mime_c = foto_costas.content_type if foto_costas else "image/jpeg"
    foto_frente_b64 = base64.b64encode(await foto_frente.read()).decode() if foto_frente else None
    foto_lado_b64 = base64.b64encode(await foto_lado.read()).decode() if foto_lado else None
    foto_costas_b64 = base64.b64encode(await foto_costas.read()).decode() if foto_costas else None
    resultado = await analisar_postural(foto_frente_b64, foto_lado_b64, foto_costas_b64, mime_f, mime_l, mime_c)
    if resultado.erro:
        raise HTTPException(status_code=500, detail=resultado.erro)
    aval = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno.id).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    if not aval:
        aval = AvaliacaoFisica(aluno_id=aluno.id, data_avaliacao=date.today())
        db.add(aval)
    aval.postura_cabeca = resultado.cabeca
    aval.postura_ombros = resultado.ombros
    aval.postura_coluna = resultado.coluna
    aval.postura_quadril = resultado.quadril
    aval.postura_joelhos = resultado.joelhos
    aval.postura_pes = resultado.pes
    aval.postura_observacoes = resultado.observacoes
    import json as _json
    if resultado.recomendacoes:
        aval.observacoes = _json.dumps(resultado.recomendacoes, ensure_ascii=False)
    db.commit()
    return {"mensagem": "Analise postural concluida!", "desvios": {"cabeca": resultado.cabeca, "ombros": resultado.ombros, "coluna": resultado.coluna, "quadril": resultado.quadril, "joelhos": resultado.joelhos, "pes": resultado.pes}, "observacoes": resultado.observacoes, "achados": resultado.achados, "recomendacoes": resultado.recomendacoes}

@router.get("/treino-hoje")
async def treino_hoje(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.treino import PlanoTreino, SessaoTreino, ExercicioSessao
    plano = db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno.id, PlanoTreino.ativo == True).first()
    if not plano:
        return {"mensagem": "Nenhum plano ativo. Faca o onboarding primeiro!"}
    dia_semana = date.today().weekday()
    sessao = db.query(SessaoTreino).filter(SessaoTreino.plano_id == plano.id, SessaoTreino.dia_semana == dia_semana).first()
    if not sessao:
        return {"mensagem": "Hoje e dia de descanso!", "dica": "Aproveite para fazer mobilidade ou caminhada leve."}
    exercicios = db.query(ExercicioSessao).filter(ExercicioSessao.sessao_id == sessao.id).order_by(ExercicioSessao.ordem).all()
    from app.routers.treino import Exercicio
    lista_ex = [{"ordem": e.ordem, "nome": db.query(Exercicio).filter(Exercicio.id == e.exercicio_id).first().nome if e.exercicio_id else "", "series": e.series, "repeticoes": e.repeticoes, "carga": e.carga_kg, "descanso": e.tempo_descanso_seg, "corretivo": False} for e in exercicios]
    from app.routers.avaliacao import AvaliacaoFisica
    aval = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno.id).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    corretivos = []
    if aval and aval.postura_observacoes:
        import json as _json
        try:
            recs = _json.loads(aval.postura_observacoes) if aval.postura_observacoes.startswith("[") else []
        except:
            recs = []
        if not recs and aval.postura_cabeca:
            recs_raw = []
            for campo in [aval.postura_cabeca, aval.postura_ombros, aval.postura_coluna, aval.postura_quadril, aval.postura_joelhos, aval.postura_pes]:
                if campo: recs_raw.append(campo)
        corretivos = ["Exercicios corretivos posturais"]
    return {"sessao": sessao.nome, "data": str(date.today()), "exercicios": lista_ex, "corretivos_posturais": corretivos, "postura_resumo": {"cabeca": aval.postura_cabeca if aval else None, "ombros": aval.postura_ombros if aval else None, "coluna": aval.postura_coluna if aval else None} if aval else None}

@router.post("/presenca")
async def registrar_presenca(dados: PresencaSchema, aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.treino import PresencaTreino, PlanoTreino
    plano = db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno.id, PlanoTreino.ativo == True).first()
    presenca = PresencaTreino(aluno_id=aluno.id, personal_id=1, plano_id=plano.id if plano else None, sessao_id=dados.sessao_id, data_presenca=date.today(), presente=True, duracao_minutos=dados.duracao_minutos, observacao=dados.observacao)
    db.add(presenca)
    db.commit()
    return {"mensagem": "Presenca registrada! Continue assim!", "data": str(date.today())}

@router.get("/dashboard")
async def dashboard(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PresencaTreino
    avals = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno.id).order_by(AvaliacaoFisica.data_avaliacao).all()
    evolucao = [{"data": str(a.data_avaliacao), "peso": a.peso, "percentual_gordura": a.percentual_gordura, "massa_magra_kg": a.massa_magra_kg, "imc": a.imc} for a in avals if a.peso]
    trinta_dias = date.today() - timedelta(days=30)
    presencas_30 = db.query(PresencaTreino).filter(PresencaTreino.aluno_id == aluno.id, PresencaTreino.data >= trinta_dias, PresencaTreino.presente == True).count()
    ultima_aval = avals[-1] if avals else None
    dias_ultima = (date.today() - ultima_aval.data_avaliacao).days if ultima_aval else None
    proxima = str(ultima_aval.data_avaliacao + timedelta(days=60)) if ultima_aval else None
    alerta = date.today() >= (ultima_aval.data_avaliacao + timedelta(days=60)) if ultima_aval else False
    return {"aluno": {"nome": aluno.nome, "objetivo": aluno.objetivo.value if aluno.objetivo else None}, "resumo": {"total_avaliacoes": len(avals), "presencas_30_dias": presencas_30, "dias_ultima_aval": dias_ultima, "alerta_reavaliacao": alerta, "proxima_reavaliacao": proxima}, "evolucao_composicao": evolucao}

@router.get("/reavaliacao")
async def verificar_reavaliacao(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.avaliacao import AvaliacaoFisica
    ultima = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno.id).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    if not ultima:
        return {"precisa_reavaliar": True, "mensagem": "Faca sua primeira avaliacao!"}
    dias = (date.today() - ultima.data_avaliacao).days
    proxima = ultima.data_avaliacao + timedelta(days=60)
    faltam = (proxima - date.today()).days
    if dias >= 60:
        return {"precisa_reavaliar": True, "dias_desde_ultima": dias, "mensagem": f"Ja faz {dias} dias! Hora de reavaliar!"}
    return {"precisa_reavaliar": False, "dias_desde_ultima": dias, "faltam_dias": faltam, "proxima_data": str(proxima)}

@router.post("/chat")
async def chat_aluno(dados: ChatSchema, aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.motor.ia_chatbot import montar_contexto, responder_chatbot, resposta_rapida
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PlanoTreino, PresencaTreino
    rapida = resposta_rapida(dados.mensagem, {"nome": aluno.nome})
    if rapida:
        return {"resposta": rapida}
    avals = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno.id).order_by(AvaliacaoFisica.data_avaliacao.desc()).limit(3).all()
    plano = db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno.id, PlanoTreino.ativo == True).first()
    trinta_dias = date.today() - timedelta(days=30)
    presencas_30 = db.query(PresencaTreino).filter(PresencaTreino.aluno_id == aluno.id, PresencaTreino.data >= trinta_dias, PresencaTreino.presente == True).count()
    aluno_dict = {"nome": aluno.nome, "objetivo": aluno.objetivo.value if aluno.objetivo else "hipertrofia", "nivel": aluno.nivel_experiencia.value if aluno.nivel_experiencia else "iniciante"}
    avals_dict = [{"data": str(a.data_avaliacao), "peso": a.peso, "percentual_gordura": a.percentual_gordura} for a in avals]
    treino_dict = {"nome": plano.nome, "objetivo": plano.objetivo} if plano else {}
    presencas_dict = {"frequencia_pct": round(presencas_30 / 30 * 100, 1)}
    contexto = montar_contexto(aluno_dict, avals_dict, treino_dict, {}, presencas_dict)
    idiomas = {"pt": "Responda SEMPRE em Portugues do Brasil.", "en": "Always respond in English.", "es": "Responde SIEMPRE en Espanol."}
    idioma_instrucao = idiomas.get(dados.idioma or "pt", idiomas["pt"])
    contexto_final = idioma_instrucao + "\n" + contexto
    resposta = await responder_chatbot(mensagem=dados.mensagem, historico=dados.historico or [], contexto=contexto_final, nome_personal="seu programa")
    return {"resposta": resposta}


@router.get("/resultado")
def resultado(aluno: AlunoCredencial = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.avaliacao import AvaliacaoFisica
    from app.models import Aluno
    aluno_obj = db.query(Aluno).filter(Aluno.id == aluno.aluno_id).first()
    if not aluno_obj:
        return {"detail": "Aluno nao encontrado"}
    avals = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.aluno_id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).all()
    if not avals:
        return {"detail": "Sem avaliacoes"}
    atual = avals[0]
    anterior = avals[1] if len(avals) > 1 else None
    variacao_peso = None
    if anterior and atual.peso and anterior.peso:
        variacao_peso = round(float(atual.peso) - float(anterior.peso), 1)
    massa_magra = None
    if atual.peso and atual.percentual_gordura:
        massa_magra = round(float(atual.peso) * (1 - float(atual.percentual_gordura)/100), 1)
    return {
        "peso_atual": float(atual.peso) if atual.peso else None,
        "percentual_gordura": float(atual.percentual_gordura) if atual.percentual_gordura else None,
        "massa_magra": massa_magra,
        "variacao_peso": variacao_peso,
        "data": str(atual.data_avaliacao)
    }


@router.get("/periodizacao")
def periodizacao(aluno: AlunoCredencial = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.models import Aluno
    aluno_obj = db.query(Aluno).filter(Aluno.id == aluno.aluno_id).first()
    if not aluno_obj:
        return {"detail": "Aluno nao encontrado"}
    objetivo = aluno_obj.objetivo.value if aluno_obj.objetivo else "hipertrofia"
    nivel = aluno_obj.nivel_experiencia.value if aluno_obj.nivel_experiencia else "intermediario"
    ciclos_map = {
        "hipertrofia": [
            {"emoji":"💪","nome":"FASE 1 — ADAPTACAO","descricao":"Semanas 1-4 · Base muscular","detalhes":"Volume moderado\nIntensidade 60-70% 1RM\nFoco em tecnica e postura\n3-4x por semana"},
            {"emoji":"🔥","nome":"FASE 2 — HIPERTROFIA","descricao":"Semanas 5-12 · Crescimento","detalhes":"Volume alto\nIntensidade 70-85% 1RM\nProgressao de carga semanal\n4-5x por semana"},
            {"emoji":"⚡","nome":"FASE 3 — INTENSIFICACAO","descricao":"Semanas 13-16 · Forca","detalhes":"Volume baixo\nIntensidade 85-95% 1RM\nMetodos avancados\n4x por semana"},
            {"emoji":"😴","nome":"FASE 4 — DELOAD","descricao":"Semana 17 · Recuperacao","detalhes":"Volume 50% do normal\nIntensidade reduzida\nFoco em mobilidade\n3x por semana"},
        ],
        "emagrecimento": [
            {"emoji":"🏃","nome":"FASE 1 — ATIVACAO","descricao":"Semanas 1-4 · Queima inicial","detalhes":"Cardio moderado\nTreino funcional\nDeficit calorico leve\n4x por semana"},
            {"emoji":"🔥","nome":"FASE 2 — ACELERACAO","descricao":"Semanas 5-10 · Queima intensa","detalhes":"HIIT 2x semana\nMusculacao 3x\nDeficit calorico moderado\n5x por semana"},
            {"emoji":"💪","nome":"FASE 3 — MANUTENCAO","descricao":"Semanas 11-16 · Preservar musculo","detalhes":"Foco em forca\nCardio steady state\nDieta de manutencao\n4x por semana"},
        ],
        "condicionamento": [
            {"emoji":"🫀","nome":"FASE 1 — BASE AEROBICA","descricao":"Semanas 1-6 · Cardio base","detalhes":"Zona 2 predominante\nFC 60-70% max\n30-45min por sessao\n4x por semana"},
            {"emoji":"⚡","nome":"FASE 2 — POTENCIA","descricao":"Semanas 7-12 · Intensidade","detalhes":"Intervalados\nFC 80-90% max\nVO2max em foco\n5x por semana"},
        ],
    }
    ciclos = ciclos_map.get(objetivo, ciclos_map["hipertrofia"])
    return {"objetivo": objetivo, "nivel": nivel, "ciclos": ciclos}
