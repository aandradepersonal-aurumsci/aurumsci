"""
Onboarding Express - Sistema de convite via link publico.

Personal gera link unico → envia pelos alunos via WhatsApp.
Aluno preenche questionario → sistema cria conta + treino base + emails.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets
import os

from app.database import get_db
from app.models import Personal, Aluno, OnboardingLink
from app.routers.app_personal import get_personal_atual

router = APIRouter(tags=["Onboarding Express"])


# ============================================================
# ROTAS DO PERSONAL (autenticadas)
# ============================================================

@router.post("/app-personal/onboarding/gerar-link")
def gerar_link_onboarding(
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """Gera ou recupera link unico do personal pra convidar alunos."""
    
    # Verifica se ja tem link ativo
    link = db.query(OnboardingLink).filter(
        OnboardingLink.personal_id == personal.id,
        OnboardingLink.ativo == True
    ).first()
    
    # Se nao tem, cria novo
    if not link:
        token = secrets.token_urlsafe(16)  # gera token aleatorio seguro
        link = OnboardingLink(
            personal_id=personal.id,
            token=token,
            ativo=True,
            total_usos=0
        )
        db.add(link)
        db.commit()
        db.refresh(link)
    
    base_url = os.getenv("BASE_URL", "https://www.aurumsc.com.br")
    
    return {
        "ok": True,
        "token": link.token,
        "url": f"{base_url}/onboarding/{link.token}",
        "total_usos": link.total_usos,
        "criado_em": link.criado_em.isoformat() if link.criado_em else None,
        "mensagem_whatsapp": (
            f"Olá! 🏆\n\n"
            f"Bem-vindo(a) à *família AurumSci*!\n\n"	 
            f"📱 Preencha seu cadastro em apenas 3 minutos e *já receba seu treino* pra começar hoje mesmo:\n\n"
            f"{base_url}/onboarding/{link.token}\n\n"
            f"💡 Como funciona:\n"
            f"✅ Você preenche o questionário (3 min)\n"
            f"✅ Recebe um treino base por email\n"
            f"✅ Já começa a treinar imediatamente\n"
	    f"✅ Após sua avaliação completa, seu treino fica 100% específico pra você\n\n"
            f"Qualquer dúvida, me chame!\n"
            f"— {personal.nome}"
        )
    }


@router.get("/app-personal/onboarding/stats")
def stats_onboarding(
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """Retorna estatisticas do onboarding do personal."""
    
    link = db.query(OnboardingLink).filter(
        OnboardingLink.personal_id == personal.id,
        OnboardingLink.ativo == True
    ).first()
    
    if not link:
        return {"total_usos": 0, "alunos_recentes": []}
    
    # Pega alunos criados via onboarding (filtragem ampla aqui pq nao temos campo origem ainda)
    alunos_recentes = db.query(Aluno).filter(
        Aluno.personal_id == personal.id
    ).order_by(Aluno.id.desc()).limit(10).all()
    
    return {
        "total_usos": link.total_usos,
        "alunos_recentes": [
            {
                "id": a.id,
                "nome": a.nome,
                "email": a.email,
                "criado_em": a.criado_em.isoformat() if hasattr(a, "criado_em") and a.criado_em else None,
            }
            for a in alunos_recentes
        ]
    }


# ============================================================
# ROTAS PUBLICAS (sem autenticacao - aluno preenchendo questionario)
# ============================================================

class QuestionarioPayload(BaseModel):
    nome: str
    email: EmailStr
    cpf: str
    data_nascimento: Optional[str] = None
    sexo: Optional[str] = None
    patologias: Optional[list] = []
    lesoes_anteriores: Optional[str] = ""
    tipo_nf: str  # "cpf" ou "cnpj"
    cnpj: Optional[str] = None
    objetivo: str  # "hipertrofia", "emagrecimento", "condicionamento"
    dias_semana: int  # 2, 3, 4, 5, 6
    nivel: str  # "iniciante", "intermediario", "avancado"
    par_q_cardiaco: bool
    par_q_dor_peito: bool
    par_q_dor_articular: bool
    par_q_medicacao: bool
    medicacao_qual: Optional[str] = None


# ============================================================
# ROTAS DO ALUNO AUTONOMO (publicas, sem personal vinculado)
# ============================================================

@router.post("/onboarding/auto/gerar-link")
def gerar_link_autonomo(db: Session = Depends(get_db)):
    """
    Gera link de onboarding SEM personal vinculado (aluno autonomo - Porta B).
    Usado por:
    - Stripe webhook apos pagamento confirmado (FASE 2)
    - Pagina publica /comecar do AurumSci (futuro)
    
    FIX 16/05/2026: criado para aluno autonomo. Mantem PRO intocado.
    """
    
    # Cria novo token sempre (cada link e unico por uso)
    token = secrets.token_urlsafe(16)
    link = OnboardingLink(
        personal_id=None,  # NULL = aluno autonomo (fix nullable=True em models)
        token=token,
        ativo=True,
        total_usos=0
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    
    base_url = os.getenv("BASE_URL", "https://www.aurumsc.com.br")
    
    return {
        "ok": True,
        "token": link.token,
        "url": f"{base_url}/onboarding/{link.token}",
        "tipo": "autonomo",
        "criado_em": link.criado_em.isoformat() if link.criado_em else None,
    }


@router.get("/onboarding/{token}", response_class=HTMLResponse)
def pagina_onboarding(token: str, db: Session = Depends(get_db)):
    """Serve pagina HTML publica do questionario."""
    
    link = db.query(OnboardingLink).filter(
        OnboardingLink.token == token,
        OnboardingLink.ativo == True
    ).first()
    
    if not link:
        return HTMLResponse(
            content="<h1>Link inválido ou expirado</h1><p>Entre em contato com seu personal.</p>",
            status_code=404
        )
    
    # Serve o HTML estatico (vamos criar depois)
    html_path = "static/onboarding.html"
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        # FIX 16/05/2026 (PATCH 5): suporta aluno autonomo no HTML
        if link.personal_id is not None:
            # Fluxo PRO: aluno convidado pelo personal
            personal = db.query(Personal).filter(Personal.id == link.personal_id).first()
            nome_personal = personal.nome if personal else "Seu Personal"
            # FIX 17/05/2026: usa data-i18n pra ser traduzido pelo frontend
            boas_vindas = f'<span data-i18n="convidadoPor" data-personal="{nome_personal}">Voce foi convidado por <strong>{nome_personal}</strong></span>'
        else:
            # Fluxo AUTONOMO: chegou pelo link direto (Stripe, pagina publica)
            boas_vindas = '<span data-i18n="bemVindoFamilia">Bem-vindo a familia <strong>AurumSci</strong> 🏆</span>'
        
        
        html = html.replace("{{BOAS_VINDAS_TEXTO}}", boas_vindas)
        html = html.replace("{{TOKEN}}", token)
        return HTMLResponse(content=html)
    
    return HTMLResponse(content="<h1>Pagina em construcao</h1>")


@router.post("/onboarding/{token}/responder")
def responder_questionario(
    token: str,
    dados: QuestionarioPayload,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Recebe respostas do questionario, cria aluno + gera treino base + manda emails.
    FIX 16/05/2026: suporta aluno autonomo (link.personal_id=None).
    """
    
    # 1. Valida token
    link = db.query(OnboardingLink).filter(
        OnboardingLink.token == token,
        OnboardingLink.ativo == True
    ).first()
    
    if not link:
        raise HTTPException(404, "Link invalido ou expirado")
    
    # FIX 16/05/2026: aluno autonomo nao tem personal vinculado
    tem_personal = link.personal_id is not None
    personal = None
    if tem_personal:
        personal = db.query(Personal).filter(Personal.id == link.personal_id).first()
        if not personal:
            raise HTTPException(404, "Personal nao encontrado")
    
    # Variaveis ternarias para uso em multiplos pontos:
    nome_quem_contata = personal.nome if personal else "Equipe AurumSci"
    email_destinatario_personal = personal.email if personal else None
    personal_id_aluno = personal.id if personal else None
    
    # 2. Limpa CPF (so numeros) - movido pra cima
    cpf_limpo = "".join(filter(str.isdigit, dados.cpf))
    if len(cpf_limpo) != 11:
        raise HTTPException(400, "CPF invalido")
    
    # 3. Verifica se aluno ja existe (busca por EMAIL ou CPF)
    # FIX 17/05/2026: busca por CPF tambem, nao so email
    # Causa raiz da duplicata de 16/05: aluno autonomo podia digitar email diferente
    # do pagamento e sistema criava duplicata
    aluno_existente = db.query(Aluno).filter(Aluno.email == dados.email).first()
    if not aluno_existente:
        aluno_existente = db.query(Aluno).filter(Aluno.cpf == cpf_limpo).first()
    
    aluno_para_atualizar = None
    if aluno_existente:
        if not tem_personal:
            # Fluxo AUTONOMO: aluno ja foi criado na landing (pagamento Stripe)
            # Aqui ele esta COMPLETANDO o cadastro pelo link do email
            aluno_para_atualizar = aluno_existente
        else:
            # Fluxo PRO: email/CPF duplicado e bloqueio mesmo
            raise HTTPException(
                400,
                "Email ou CPF ja cadastrado. Se voce ja e aluno do AurumSci, faca login no app."
            )
    
    
    # 4. Verifica PAR-Q (saude)
    tem_risco = (
        dados.par_q_cardiaco or 
        dados.par_q_dor_peito or 
        dados.par_q_dor_articular or 
        dados.par_q_medicacao
    )
    
    # 5. Cria aluno (vinculado ao personal OU autonomo)
    data_nasc_obj = None
    if dados.data_nascimento:
        try:
            from datetime import datetime as _dt
            data_nasc_obj = _dt.strptime(dados.data_nascimento, "%Y-%m-%d").date()
        except Exception:
            data_nasc_obj = None
    
    from app.models import Sexo as _Sexo
    sexo_obj = None
    if dados.sexo == "M":
        sexo_obj = _Sexo.MASCULINO
    elif dados.sexo == "F":
        sexo_obj = _Sexo.FEMININO
    
    # FIX 16/05/2026: ATUALIZA aluno existente (autonomo) OU CRIA novo (PRO)
    if aluno_para_atualizar:
        # Aluno autonomo completando cadastro (ja pagou na landing)
        aluno_para_atualizar.cpf = cpf_limpo
        aluno_para_atualizar.objetivo = dados.objetivo.upper() if dados.objetivo else None
        aluno_para_atualizar.nivel_experiencia = dados.nivel.upper() if dados.nivel else None
        aluno_para_atualizar.data_nascimento = data_nasc_obj
        aluno_para_atualizar.sexo = sexo_obj
        if dados.nome and not aluno_para_atualizar.nome:
            aluno_para_atualizar.nome = dados.nome
        novo_aluno = aluno_para_atualizar
        db.flush()
    else:
        # Novo aluno (PRO: convite do personal | autonomo puro: sem cadastro previo)
        novo_aluno = Aluno(
            nome=dados.nome,
            email=dados.email,
            cpf=cpf_limpo,
            personal_id=personal_id_aluno,
            ativo=True,
            objetivo=dados.objetivo.upper() if dados.objetivo else None,
            nivel_experiencia=dados.nivel.upper() if dados.nivel else None,
            data_nascimento=data_nasc_obj,
            sexo=sexo_obj,
        )
        db.add(novo_aluno)
        db.flush()
    
    # 6. Cria credencial de acesso (senha = 6 primeiros digitos do CPF)
    # FIX 16/05/2026: autonomo ja tem credencial criada na landing, so cria se nao existir
    # FIX 17/05/2026 P4: se aluno autonomo COMPLETOU cadastro, atualiza senha_hash com CPF novo
    from app.routers.portal_aluno import AlunoCredencial, pwd_context
    senha_inicial = cpf_limpo[:6]
    cred_existente = db.query(AlunoCredencial).filter(AlunoCredencial.aluno_id == novo_aluno.id).first()
    if not cred_existente:
        credencial = AlunoCredencial(
            aluno_id=novo_aluno.id,
            email=dados.email,
            senha_hash=pwd_context.hash(senha_inicial)
        )
        db.add(credencial)
    elif aluno_para_atualizar:
        # Autonomo completando cadastro: atualiza senha pra refletir CPF novo
        cred_existente.senha_hash = pwd_context.hash(senha_inicial)
        cred_existente.email = dados.email
    
    # 7. Atualiza contador do link
    link.total_usos += 1
    
    # Cria anamnese inicial com patologias + lesoes
    if dados.patologias or dados.lesoes_anteriores:
        try:
            from app.routers.anamnese import Anamnese
            from datetime import date as _date
            patologias_str = ",".join(dados.patologias) if dados.patologias else ""
            anam = Anamnese(
                aluno_id=novo_aluno.id,
                data_avaliacao=_date.today(),
                doencas_cronicas=patologias_str,
                lesoes_anteriores=dados.lesoes_anteriores or "",
                medicamentos_uso=dados.medicacao_qual or "" if hasattr(dados, "medicacao_qual") else ""
            )
            db.add(anam)
        except Exception as e:
            print(f"[ONBOARDING] Erro criar anamnese: {e}")
    
    db.commit()
    db.refresh(novo_aluno)
    
    # 8. Gera treino base (se PAR-Q ok)
    treino_gerado = False
    if not tem_risco:
        try:
            from app.motor.periodizacao import gerar_periodizacao, periodizacao_to_dict
            from app.routers.treino import PlanoTreino, SessaoTreino, Exercicio
            from datetime import date
            import json
            
            periodizacao = gerar_periodizacao(
                objetivo=dados.objetivo if dados.objetivo else None,
                nivel=dados.nivel,
                dias_semana=dados.dias_semana,
                semanas_total=12,
                data_inicio=date.today(),
                tipo_periodizacao="ondulatoria"
            )
            periodo_dict = periodizacao_to_dict(periodizacao)
            
            plano = PlanoTreino(
                aluno_id=novo_aluno.id,
                personal_id=personal_id_aluno,
                nome=f"Plano {dados.objetivo.capitalize()} - {dados.nivel.capitalize()}",
                objetivo=dados.objetivo.upper() if dados.objetivo else None,
                nivel=dados.nivel,
                dias_semana=dados.dias_semana,
                semanas_total=12,
                data_inicio=date.today(),
                ativo=True,
                periodizacao=json.dumps(periodo_dict, ensure_ascii=False)
            )
            db.add(plano)
            db.flush()
            
            # FIX 18/05/2026: importa ExercicioSessao + Exercicio + cria os exercicios da sessao
            from app.routers.treino import ExercicioSessao
            
            for i, sessao_p in enumerate(periodizacao.sessoes_prescritas):
                sessao = SessaoTreino(
                    plano_id=plano.id,
                    nome=sessao_p.nome,
                    dia_semana=i + 1
                )
                db.add(sessao)
                db.flush()  # gera sessao.id
                
                # Cria exercicios da sessao
                for ex_p in sessao_p.exercicios:
                    # Procura ou cria exercicio no banco
                    ex_obj = db.query(Exercicio).filter(Exercicio.nome == ex_p.nome).first()
                    if not ex_obj:
                        ex_obj = Exercicio(nome=ex_p.nome, grupo_muscular=ex_p.grupo)
                        db.add(ex_obj)
                        db.flush()
                    
                    # Cria o vinculo ExercicioSessao
                    es = ExercicioSessao(
                        sessao_id=sessao.id,
                        exercicio_id=ex_obj.id,
                        ordem=ex_p.ordem,
                        series=ex_p.series,
                        repeticoes=ex_p.repeticoes,
                        tempo_descanso_seg=ex_p.descanso_segundos,
                        observacoes=ex_p.tecnica_especial or ""
                    )
                    db.add(es)
            
            db.commit()
            treino_gerado = True
        except Exception as e:
            print(f"[ONBOARDING] Erro gerar treino: {e}")
    
    # 9. Manda emails (aluno + personal SE houver)
    try:
        from app.services.email_service import enviar_email
        
        # Email pro ALUNO
        if treino_gerado:
            assunto_aluno = "🏆 Bem-vindo à família AurumSci! Seu treino está pronto"
            proximo_passo_aluno = (
                f"Marque sua avaliação presencial com {nome_quem_contata} pra refinar 100% pra você!"
                if tem_personal else
                "Acesse o app e comece a treinar. Sua próxima avaliação será em 8 semanas."
            )
            corpo_aluno = f"""
            <h2>Bem-vindo, {dados.nome}! 🏆</h2>
            <p>Seu cadastro foi feito com sucesso e seu <b>treino base já está pronto</b>!</p>
            <p>📱 <b>Acesse o app:</b> https://www.aurumsc.com.br/aluno</p>
            <p>📧 <b>Email:</b> {dados.email}</p>
            <p>🔑 <b>Senha inicial:</b> {senha_inicial} (6 primeiros do seu CPF)</p>
            <p><b>Próximo passo:</b> {proximo_passo_aluno}</p>
            <p>Bons treinos! 💪</p>
            <p>— Equipe AurumSci</p>
            """
        else:
            assunto_aluno = "Cadastro recebido - Aguardando avaliação"
            contato_aluno = (
                f"<b>{nome_quem_contata} entrará em contato em até 24h</b>"
                if tem_personal else
                "<b>Nossa equipe entrará em contato em até 24h</b>"
            )
            corpo_aluno = f"""
            <h2>Olá, {dados.nome}! 👋</h2>
            <p>Recebemos seu cadastro com sucesso!</p>
            <p>Como você indicou alguma condição de saúde, {contato_aluno} para uma avaliação personalizada antes de iniciar os treinos.</p>
            <p>📱 <b>Seu acesso:</b> https://www.aurumsc.com.br/aluno</p>
            <p>📧 <b>Email:</b> {dados.email}</p>
            <p>🔑 <b>Senha:</b> {senha_inicial}</p>
            <p>— Equipe AurumSci</p>
            """
        
        enviar_email(dados.email, assunto_aluno, corpo_aluno)
        
        # Email pro PERSONAL (SO se tem personal)
        if email_destinatario_personal:
            if tem_risco:
                assunto_personal = f"⚠️ Novo aluno com atenção: {dados.nome}"
                corpo_personal = f"""
                <h2>⚠️ Novo aluno preencheu o onboarding</h2>
                <p><b>Nome:</b> {dados.nome}</p>
                <p><b>Email:</b> {dados.email}</p>
                <p><b>Objetivo:</b> {dados.objetivo}</p>
                <p><b>ATENÇÃO - Indicou condição de saúde:</b></p>
                <ul>
                    {f'<li>Problema cardíaco</li>' if dados.par_q_cardiaco else ''}
                    {f'<li>Dor no peito ao exercitar</li>' if dados.par_q_dor_peito else ''}
                    {f'<li>Dor articular</li>' if dados.par_q_dor_articular else ''}
                    {f'<li>Medicação contínua: {dados.medicacao_qual or "não especificada"}</li>' if dados.par_q_medicacao else ''}
                </ul>
                <p><b>Treino NÃO foi gerado automaticamente.</b> Recomendamos avaliação presencial antes de iniciar.</p>
                """
            else:
                assunto_personal = f"🎉 Novo aluno: {dados.nome}"
                corpo_personal = f"""
                <h2>🎉 Você ganhou um novo aluno!</h2>
                <p><b>Nome:</b> {dados.nome}</p>
                <p><b>Email:</b> {dados.email}</p>
                <p><b>Objetivo:</b> {dados.objetivo}</p>
                <p><b>Nível:</b> {dados.nivel}</p>
                <p><b>Frequência:</b> {dados.dias_semana}x por semana</p>
                <p>✅ Treino base já foi criado automaticamente.</p>
                <p>Acesse o app PRO pra ajustar e marcar a avaliação presencial.</p>
                """
            
            enviar_email(email_destinatario_personal, assunto_personal, corpo_personal)
    except Exception as e:
        print(f"[ONBOARDING] Erro enviar email: {e}")
    
    # Mensagem final adaptada
    if treino_gerado:
        mensagem_final = "Tudo certo! Seu treino tá pronto, confira seu email!"
    elif tem_personal:
        mensagem_final = f"Cadastro recebido! {nome_quem_contata} entrará em contato em até 24h."
    else:
        mensagem_final = "Cadastro recebido! Nossa equipe entrará em contato em até 24h."
    
    return {
        "ok": True,
        "aluno_id": novo_aluno.id,
        "treino_gerado": treino_gerado,
        "tem_risco": tem_risco,
        "tipo": "pro" if tem_personal else "autonomo",
        "mensagem": mensagem_final
    }
