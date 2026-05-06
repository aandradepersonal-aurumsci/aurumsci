"""
Servico de geracao de PDF do contrato AurumSci-Personal.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
import os


def gerar_pdf_contrato(personal, output_dir="static/contratos"):
    """Gera PDF do contrato AurumSci-Personal com dados preenchidos."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"contrato_personal_{personal.id}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Cria documento
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#C9A961'),
        alignment=TA_CENTER,
        spaceAfter=8
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    secao_style = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=HexColor('#C9A961'),
        spaceBefore=14,
        spaceAfter=8
    )
    
    texto_style = ParagraphStyle(
        'Texto',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14
    )
    
    # Conteudo
    story = []
    
    # Titulo
    story.append(Paragraph("CONTRATO DE PRESTAÇÃO DE SERVIÇOS", titulo_style))
    story.append(Paragraph(f"AurumSci PRO · Versão 1.0 · {datetime.now().strftime('%d/%m/%Y')}", subtitulo_style))
    
    # Dados das partes
    dados_data = [
        ['CONTRATANTE (AurumSci)', ''],
        ['CNPJ:', '58.893.821/0001-84'],
        ['Razão Social:', 'AurumSci Tecnologia'],
        ['', ''],
        ['CONTRATADO (Personal Trainer)', ''],
        ['Nome:', personal.nome or '—'],
        ['Email:', personal.email or '—'],
        ['CREF:', f"{personal.cref}" + (f" - {personal.cref_estado}" if personal.cref_estado else '')],
        ['CPF:', personal.cpf or '—'],
        ['Telefone:', personal.telefone or '—'],
    ]
    
    tabela = Table(dados_data, colWidths=[5*cm, 12*cm])
    tabela.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), black),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,4), (0,4), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,0), HexColor('#C9A961')),
        ('TEXTCOLOR', (0,4), (0,4), HexColor('#C9A961')),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#F5F5F0')),
        ('BACKGROUND', (0,4), (-1,4), HexColor('#F5F5F0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 16))
    
    # Clausulas
    story.append(Paragraph("1. OBJETO", secao_style))
    story.append(Paragraph(
        "Plataforma SaaS para gestão profissional de personal trainers e seus alunos, "
        "incluindo: cadastro, avaliação, treinos, cobrança e relacionamento.",
        texto_style
    ))
    
    story.append(Paragraph("2. PLANOS E MENSALIDADE", secao_style))
    story.append(Paragraph(
        "<b>Bronze:</b> R$ 49,90/mês (até 10 alunos)<br/>"
        "<b>Prata:</b> R$ 89,90/mês (até 20 alunos)<br/>"
        "<b>Ouro:</b> R$ 149,90/mês (até 50 alunos)<br/>"
        "<b>Diamante:</b> R$ 249,90/mês (alunos ilimitados)<br/><br/>"
        "Cobrança automática via cartão. Upgrade/downgrade a qualquer momento.",
        texto_style
    ))
    
    story.append(Paragraph("3. VALIDAÇÃO PROFISSIONAL", secao_style))
    story.append(Paragraph(
        "3.1 Acesso EXCLUSIVO a profissionais com registro ATIVO e ADIMPLENTE no CREF.<br/><br/>"
        "3.2 Personal declara, sob as penas da lei (Art. 299 CP — Falsidade Ideológica), que:<br/>"
        "a) CREF informado é seu, ativo e adimplente;<br/>"
        "b) Consultou o site oficial do CONFEF (www.confef.org.br);<br/>"
        "c) Não responde a processo ético em andamento.<br/><br/>"
        "3.3 AurumSci pode validar o registro a qualquer momento. Irregularidade detectada "
        "suspende o acesso sem reembolso.",
        texto_style
    ))
    
    story.append(Paragraph("4. CUSTOS DE TERCEIROS", secao_style))
    story.append(Paragraph(
        "Serviços automatizados têm custo repassado sem margem:<br/>"
        "• WhatsApp (Meta): R$ 0,12 por mensagem<br/>"
        "• NF-e (prefeitura): R$ 0,30 por nota<br/><br/>"
        "Consumo visível em tempo real no painel financeiro.",
        texto_style
    ))
    
    story.append(Paragraph("5. TRIAL E CANCELAMENTO", secao_style))
    story.append(Paragraph(
        "Trial gratuito de 7 dias. Após esse período, cobrança automática mensal. "
        "Cancelamento a qualquer momento, com acesso ativo até o fim do ciclo pago.",
        texto_style
    ))
    
    story.append(Paragraph("6. RESPONSABILIDADE TÉCNICA", secao_style))
    story.append(Paragraph(
        "AurumSci é ferramenta tecnológica. O personal CREF é o ÚNICO responsável "
        "por treinos, avaliações e atendimentos. Sugestões geradas por IA (treinos, "
        "postural, nutrição) são referenciais e exigem supervisão profissional.",
        texto_style
    ))
    
    story.append(Paragraph("7. PROTEÇÃO DE DADOS (LGPD)", secao_style))
    story.append(Paragraph(
        "Dados dos alunos pertencem ao personal. AurumSci não comercializa nem "
        "compartilha. Personal pode exportar/excluir dados a qualquer momento.",
        texto_style
    ))
    
    story.append(Paragraph("8. JURISDIÇÃO", secao_style))
    story.append(Paragraph(
        f"Foro da comarca de São Paulo/SP. Lei brasileira aplicável. "
        f"Versão 1.0 datada de {datetime.now().strftime('%d/%m/%Y')}.",
        texto_style
    ))
    
    # Assinatura
    story.append(Spacer(1, 20))
    
    aceite_data = [
        ['CONTRATO ACEITO DIGITALMENTE', ''],
        ['Data:', personal.contrato_aceito_em.strftime('%d/%m/%Y às %H:%M:%S') if personal.contrato_aceito_em else '—'],
        ['IP:', personal.contrato_aceito_ip or '—'],
        ['Status CREF:', personal.cref_status or 'pendente'],
        ['Consultou CONFEF:', 'Sim' if personal.cref_consultado_confef else 'Não'],
    ]
    
    aceite_table = Table(aceite_data, colWidths=[5*cm, 12*cm])
    aceite_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), black),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (0,0), 11),
        ('TEXTCOLOR', (0,0), (0,0), HexColor('#4CAF50')),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#E8F5E9')),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(aceite_table)
    
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "<i>Powered by AurumSci · Ciência, método e inteligência artificial</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=HexColor('#999999'))
    ))
    
    doc.build(story)
    
    return filepath
