"""
Gerador de Laudo PDF — Avaliação Física
Usa reportlab para gerar laudo profissional preto e dourado
"""

import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Paleta preto e dourado ────────────────────────────────────────────────────
PRETO      = colors.HexColor("#0A0A0A")
PRETO2     = colors.HexColor("#111111")
PRETO3     = colors.HexColor("#1A1A1A")
OURO       = colors.HexColor("#C9A84C")
OURO2      = colors.HexColor("#E8C97A")
OURO3      = colors.HexColor("#8B6914")
CINZA      = colors.HexColor("#A09888")
CINZA2     = colors.HexColor("#6B6358")
BRANCO     = colors.HexColor("#F0EDE8")
VERDE      = colors.HexColor("#1D9E75")
VERMELHO   = colors.HexColor("#E24B4A")
AZUL       = colors.HexColor("#378ADD")

# ── Estilos ───────────────────────────────────────────────────────────────────

def estilos():
    return {
        "titulo": ParagraphStyle("titulo", fontSize=22, textColor=OURO, fontName="Helvetica-Bold",
                                  spaceAfter=2, alignment=TA_CENTER),
        "subtitulo": ParagraphStyle("subtitulo", fontSize=11, textColor=CINZA, fontName="Helvetica",
                                     spaceAfter=8, alignment=TA_CENTER, letterSpacing=2),
        "secao": ParagraphStyle("secao", fontSize=12, textColor=OURO, fontName="Helvetica-Bold",
                                 spaceBefore=12, spaceAfter=6),
        "normal": ParagraphStyle("normal", fontSize=10, textColor=BRANCO, fontName="Helvetica",
                                  spaceAfter=4, leading=14),
        "normal_cin": ParagraphStyle("normal_cin", fontSize=10, textColor=CINZA, fontName="Helvetica",
                                      spaceAfter=4),
        "destaque": ParagraphStyle("destaque", fontSize=13, textColor=OURO2, fontName="Helvetica-Bold",
                                    spaceAfter=2, alignment=TA_CENTER),
        "rodape": ParagraphStyle("rodape", fontSize=8, textColor=CINZA2, fontName="Helvetica",
                                  alignment=TA_CENTER),
        "label": ParagraphStyle("label", fontSize=9, textColor=CINZA, fontName="Helvetica",
                                 spaceAfter=1),
        "valor": ParagraphStyle("valor", fontSize=11, textColor=BRANCO, fontName="Helvetica-Bold"),
    }


def cor_classificacao(cls):
    if not cls: return CINZA
    cls = cls.lower()
    if any(x in cls for x in ["excelente", "superior", "atleta", "bom", "boa forma", "baixo", "normal", "acima"]):
        return VERDE
    if any(x in cls for x in ["regular", "media", "aceitavel", "moderado", "sobrepeso"]):
        return OURO
    if any(x in cls for x in ["fraco", "obesidade", "alto", "abaixo do essencial"]):
        return VERMELHO
    return CINZA


# ── Componentes ───────────────────────────────────────────────────────────────

def linha_ouro():
    return HRFlowable(width="100%", thickness=0.5, color=OURO3, spaceAfter=8, spaceBefore=4)


def tabela_dois_cols(dados, estilos_):
    rows = []
    for i in range(0, len(dados), 2):
        row = []
        for j in range(2):
            if i + j < len(dados):
                label, valor, cls = dados[i + j]
                cor = cor_classificacao(cls) if cls else BRANCO
                cell = [
                    Paragraph(label, estilos_["label"]),
                    Paragraph(str(valor) if valor is not None else "—",
                              ParagraphStyle("v", fontSize=11, textColor=cor,
                                             fontName="Helvetica-Bold")),
                ]
                if cls:
                    cell.append(Paragraph(cls, ParagraphStyle("c", fontSize=8,
                                                               textColor=cor, fontName="Helvetica")))
            else:
                cell = [Paragraph("", estilos_["label"])]
            row.append(cell)
        rows.append(row)

    t = Table(rows, colWidths=[8.5 * cm, 8.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRETO2),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [PRETO2, PRETO3]),
        ("BOX", (0, 0), (-1, -1), 0.5, OURO3),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#2A2520")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def tabela_circunferencias(circ_data, estilos_):
    header = [
        Paragraph("Segmento", ParagraphStyle("h", fontSize=9, textColor=OURO,
                                              fontName="Helvetica-Bold")),
        Paragraph("Valor (cm)", ParagraphStyle("h", fontSize=9, textColor=OURO,
                                                fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]
    rows = [header]
    for nome, valor in circ_data:
        if valor is not None:
            rows.append([
                Paragraph(nome, estilos_["normal_cin"]),
                Paragraph(f"{valor:.1f} cm", ParagraphStyle("v", fontSize=10, textColor=BRANCO,
                                                              fontName="Helvetica-Bold",
                                                              alignment=TA_CENTER)),
            ])

    if len(rows) == 1:
        return None

    t = Table(rows, colWidths=[12 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), OURO3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PRETO2, PRETO3]),
        ("BOX", (0, 0), (-1, -1), 0.5, OURO3),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#2A2520")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ── Gerador principal ─────────────────────────────────────────────────────────

def gerar_laudo(avaliacao: dict, aluno: dict, personal: dict) -> bytes:
    """
    Gera o laudo em PDF e retorna os bytes.
    avaliacao: dict com todos os campos da AvaliacaoFisica
    aluno: dict com nome, data_nascimento, sexo, objetivo
    personal: dict com nome, cref
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        title=f"Laudo - {aluno.get('nome', '')}",
    )

    s = estilos()
    story = []

    # ── Cabeçalho ──────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(personal.get("nome", "Personal Trainer"), s["titulo"]),
        Paragraph(f"CREF: {personal.get('cref', '')}", s["normal_cin"]),
    ]]
    header_table = Table(header_data, colWidths=[13 * cm, 4 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRETO2),
        ("BOX", (0, 0), (-1, -1), 1, OURO),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("LAUDO DE AVALIAÇÃO FÍSICA", s["subtitulo"]))
    story.append(linha_ouro())

    # ── Dados do aluno ──────────────────────────────────────────────────────
    story.append(Paragraph("Dados do Avaliado", s["secao"]))

    data_aval = avaliacao.get("data_avaliacao", date.today())
    if isinstance(data_aval, str):
        from datetime import datetime
        data_aval = datetime.strptime(data_aval, "%Y-%m-%d").date()

    nasc = aluno.get("data_nascimento")
    idade_str = "—"
    if nasc:
        if isinstance(nasc, str):
            from datetime import datetime
            nasc = datetime.strptime(nasc, "%Y-%m-%d").date()
        hoje = date.today()
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        idade_str = f"{idade} anos"

    dados_aluno = [
        [Paragraph("Nome", s["label"]), Paragraph(aluno.get("nome", "—"), s["normal"]),
         Paragraph("Data de Avaliação", s["label"]), Paragraph(data_aval.strftime("%d/%m/%Y"), s["normal"])],
        [Paragraph("Idade", s["label"]), Paragraph(idade_str, s["normal"]),
         Paragraph("Sexo", s["label"]), Paragraph((aluno.get("sexo") or "—").capitalize(), s["normal"])],
        [Paragraph("Objetivo", s["label"]),
         Paragraph((aluno.get("objetivo") or "—").replace("_", " ").capitalize(), s["normal"]),
         Paragraph("", s["label"]), Paragraph("", s["normal"])],
    ]
    t = Table(dados_aluno, colWidths=[3 * cm, 6.5 * cm, 3.5 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRETO2),
        ("BOX", (0, 0), (-1, -1), 0.5, OURO3),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#2A2520")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # ── Composição Corporal ─────────────────────────────────────────────────
    story.append(Paragraph("Composição Corporal", s["secao"]))

    comp_dados = [
        ("Peso", f"{avaliacao.get('peso', 0):.1f} kg" if avaliacao.get("peso") else "—", None),
        ("Estatura", f"{avaliacao.get('estatura', 0):.1f} cm" if avaliacao.get("estatura") else "—", None),
        ("IMC", f"{avaliacao.get('imc', 0):.2f} kg/m²" if avaliacao.get("imc") else "—",
         avaliacao.get("classificacao_imc")),
        ("% Gordura", f"{avaliacao.get('percentual_gordura', 0):.2f}%" if avaliacao.get("percentual_gordura") else "—",
         avaliacao.get("classificacao_gordura")),
        ("Massa Gorda", f"{avaliacao.get('massa_gorda_kg', 0):.2f} kg" if avaliacao.get("massa_gorda_kg") else "—", None),
        ("Massa Magra", f"{avaliacao.get('massa_magra_kg', 0):.2f} kg" if avaliacao.get("massa_magra_kg") else "—", None),
        ("Rel. Cintura/Quadril", f"{avaliacao.get('relacao_cintura_quadril', 0):.3f}" if avaliacao.get("relacao_cintura_quadril") else "—",
         avaliacao.get("risco_cardiovascular")),
        ("Densidade Corporal", f"{avaliacao.get('densidade_corporal', 0):.4f}" if avaliacao.get("densidade_corporal") else "—", None),
    ]
    story.append(tabela_dois_cols(comp_dados, s))
    story.append(Spacer(1, 8))

    # ── Testes Físicos ──────────────────────────────────────────────────────
    story.append(Paragraph("Testes Físicos", s["secao"]))

    testes_dados = [
        ("Flexibilidade (Wells)", f"{avaliacao.get('teste_flexibilidade_cm', 0):.1f} cm" if avaliacao.get("teste_flexibilidade_cm") is not None else "—",
         avaliacao.get("classificacao_flexibilidade")),
        ("Flexão de Braço (1 min)", f"{avaliacao.get('teste_flexao_num', 0)} rep." if avaliacao.get("teste_flexao_num") is not None else "—",
         avaliacao.get("classificacao_flexao")),
        ("Barra Fixa (1 min)", f"{avaliacao.get('teste_barra_num', 0)} rep." if avaliacao.get("teste_barra_num") is not None else "—", None),
        ("Cooper 12 min", f"{avaliacao.get('teste_cooper_metros', 0):.0f} m" if avaliacao.get("teste_cooper_metros") else "—", None),
        ("VO2max (Cooper)", f"{avaliacao.get('vo2max', 0):.2f} ml/kg/min" if avaliacao.get("vo2max") else "—",
         avaliacao.get("classificacao_vo2")),
        ("", "—", None),
    ]
    story.append(tabela_dois_cols(testes_dados, s))
    story.append(Spacer(1, 8))

    # ── Circunferências ─────────────────────────────────────────────────────
    circ_campos = [
        ("Pescoço", avaliacao.get("circ_pescoco")),
        ("Tórax", avaliacao.get("circ_torax")),
        ("Cintura", avaliacao.get("circ_cintura")),
        ("Abdômen", avaliacao.get("circ_abdomen")),
        ("Quadril", avaliacao.get("circ_quadril")),
        ("Braço D. Relaxado", avaliacao.get("circ_braco_d_relaxado")),
        ("Braço D. Contraído", avaliacao.get("circ_braco_d_contraido")),
        ("Braço E. Relaxado", avaliacao.get("circ_braco_e_relaxado")),
        ("Braço E. Contraído", avaliacao.get("circ_braco_e_contraido")),
        ("Antebraço D.", avaliacao.get("circ_antebraco_d")),
        ("Antebraço E.", avaliacao.get("circ_antebraco_e")),
        ("Coxa D.", avaliacao.get("circ_coxa_d")),
        ("Coxa E.", avaliacao.get("circ_coxa_e")),
        ("Panturrilha D.", avaliacao.get("circ_panturrilha_d")),
        ("Panturrilha E.", avaliacao.get("circ_panturrilha_e")),
    ]
    circ_preenchidas = [(n, v) for n, v in circ_campos if v is not None]

    if circ_preenchidas:
        story.append(Paragraph("Circunferências", s["secao"]))
        t_circ = tabela_circunferencias(circ_preenchidas, s)
        if t_circ:
            story.append(t_circ)
            story.append(Spacer(1, 8))

    # ── Análise Postural ────────────────────────────────────────────────────
    posturas = [
        ("Cabeça", avaliacao.get("postura_cabeca")),
        ("Ombros", avaliacao.get("postura_ombros")),
        ("Coluna", avaliacao.get("postura_coluna")),
        ("Quadril", avaliacao.get("postura_quadril")),
        ("Joelhos", avaliacao.get("postura_joelhos")),
        ("Pés", avaliacao.get("postura_pes")),
    ]
    posturas_preen = [(n, v) for n, v in posturas if v]

    if posturas_preen or avaliacao.get("postura_observacoes"):
        story.append(Paragraph("Análise Postural", s["secao"]))
        for nome, valor in posturas_preen:
            row_data = [[
                Paragraph(nome, s["label"]),
                Paragraph(valor, s["normal"]),
            ]]
            t_post = Table(row_data, colWidths=[5 * cm, 12 * cm])
            t_post.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PRETO2),
                ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#2A2520")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.append(t_post)

        if avaliacao.get("postura_observacoes"):
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"Observações posturais: {avaliacao['postura_observacoes']}", s["normal_cin"]))
        story.append(Spacer(1, 8))

    # ── Observações ─────────────────────────────────────────────────────────
    if avaliacao.get("observacoes"):
        story.append(Paragraph("Observações Gerais", s["secao"]))
        story.append(Paragraph(avaliacao["observacoes"], s["normal"]))
        story.append(Spacer(1, 8))

    # ── Assinatura ──────────────────────────────────────────────────────────
    story.append(linha_ouro())
    story.append(Spacer(1, 20))

    assinatura = Table([[
        Paragraph("", s["normal"]),
        Table([[
            Paragraph("_" * 40, s["normal_cin"]),
            Paragraph(personal.get("nome", ""), s["destaque"]),
            Paragraph(f"CREF: {personal.get('cref', '')}", s["rodape"]),
        ]], colWidths=[8 * cm]),
    ]], colWidths=[9 * cm, 8 * cm])
    story.append(assinatura)

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        f"Laudo gerado em {date.today().strftime('%d/%m/%Y')} — Sistema PT Gestão Premium",
        s["rodape"]
    ))

    # ── Build ────────────────────────────────────────────────────────────────
    def primeira_pagina(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PRETO)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.restoreState()

    def demais_paginas(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PRETO)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=primeira_pagina, onLaterPages=demais_paginas)
    return buffer.getvalue()
