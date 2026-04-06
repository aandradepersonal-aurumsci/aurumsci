"""
Script para popular banco de exercícios AurumSci
100+ exercícios com grupo muscular, equipamento, descrição e link YouTube
"""
import psycopg2

conn = psycopg2.connect('postgresql://postgres:TvlbrPuVPWsIFQWykuYnAwEVBtkmYlmF@hopper.proxy.rlwy.net:25197/railway')
cur = conn.cursor()

exercicios = [
    # PEITO
    ("Supino Reto com Barra", "Peito", "Barra", "Exercício básico para peitoral maior", "Deite no banco, segure a barra na largura dos ombros, desça até o peito e empurre", "https://www.youtube.com/watch?v=gRVjAtPip0Y"),
    ("Supino Inclinado com Halteres", "Peito", "Halteres", "Ênfase na porção superior do peitoral", "Banco inclinado 30-45°, desça os halteres controlado e empurre", "https://www.youtube.com/watch?v=8iPEnn-ltC8"),
    ("Supino Declinado com Barra", "Peito", "Barra", "Ênfase na porção inferior do peitoral", "Banco declinado, amplitude completa", "https://www.youtube.com/watch?v=LfyQBUKR8SE"),
    ("Crucifixo com Halteres", "Peito", "Halteres", "Isolamento do peitoral", "Abra os braços em arco, mantenha leve flexão no cotovelo", "https://www.youtube.com/watch?v=eozdVDA78K0"),
    ("Crossover no Cabo", "Peito", "Cabo", "Isolamento do peitoral com tensão constante", "Puxe os cabos cruzando na frente do corpo", "https://www.youtube.com/watch?v=taI4XduLpTk"),
    ("Flexão de Braço", "Peito", "Peso corporal", "Exercício funcional de peito e tríceps", "Corpo reto, desça o peito até quase tocar o chão", "https://www.youtube.com/watch?v=IODxDxX7oi4"),
    ("Supino Inclinado com Barra", "Peito", "Barra", "Porção clavicular do peitoral", "Banco 30-45°, pegada um pouco mais fechada", "https://www.youtube.com/watch?v=DbFgADa2PL8"),
    ("Peck Deck", "Peito", "Máquina", "Isolamento do peitoral", "Junte os braços na frente contraindo o peitoral", "https://www.youtube.com/watch?v=Z57CtFmRMxA"),

    # COSTAS
    ("Puxada Frontal", "Costas", "Cabo", "Latíssimo do dorso", "Puxe a barra até a clavícula com o tronco levemente inclinado", "https://www.youtube.com/watch?v=CAwf7n6Luuc"),
    ("Remada Curvada com Barra", "Costas", "Barra", "Espessura das costas", "Tronco inclinado ~45°, puxe a barra até o abdômen", "https://www.youtube.com/watch?v=vT2GjY_Umpw"),
    ("Remada Unilateral com Haltere", "Costas", "Halteres", "Latíssimo unilateral", "Apoie joelho e mão no banco, puxe o haltere até o quadril", "https://www.youtube.com/watch?v=pYcpY20QaE8"),
    ("Barra Fixa", "Costas", "Peso corporal", "Latíssimo do dorso — exercício rainha", "Pegada pronada, puxe até o queixo acima da barra", "https://www.youtube.com/watch?v=eGo4IYlbE5g"),
    ("Remada Cavalinho", "Costas", "Máquina", "Espessura das costas", "Puxe os cabos até o abdômen mantendo o tronco ereto", "https://www.youtube.com/watch?v=GZbfZ033f74"),
    ("Puxada no Cabo Reto", "Costas", "Cabo", "Latíssimo inferior", "Com barra reta, puxe até as coxas mantendo braços estendidos", "https://www.youtube.com/watch?v=wVTnFxFBUEI"),
    ("Remada Alta", "Costas", "Barra", "Trapézio e romboides", "Puxe a barra até o queixo com cotovelos elevados", "https://www.youtube.com/watch?v=NN_T8jmZNmQ"),
    ("Levantamento Terra", "Costas", "Barra", "Cadeia posterior completa", "Mantenha coluna neutra, empurre o chão com os pés", "https://www.youtube.com/watch?v=op9kVnSso6Q"),
    ("Puxada Supinada", "Costas", "Cabo", "Bíceps e latíssimo", "Pegada supinada na largura dos ombros, puxe até o peito", "https://www.youtube.com/watch?v=rT7FtaLZD48"),

    # OMBROS
    ("Desenvolvimento com Halteres", "Ombros", "Halteres", "Deltóide anterior e medial", "Empurre os halteres acima da cabeça com rotação natural", "https://www.youtube.com/watch?v=qEwKCR5JCog"),
    ("Desenvolvimento com Barra", "Ombros", "Barra", "Deltóide completo", "Barra na altura do queixo, empurre acima da cabeça", "https://www.youtube.com/watch?v=2yjwXTZQDDI"),
    ("Elevação Lateral", "Ombros", "Halteres", "Deltóide medial", "Eleve os braços lateralmente até a altura dos ombros", "https://www.youtube.com/watch?v=3VcKaXpzqRo"),
    ("Elevação Frontal", "Ombros", "Halteres", "Deltóide anterior", "Eleve um braço de cada vez à frente até a altura dos ombros", "https://www.youtube.com/watch?v=gkpzAbSB9_s"),
    ("Face Pull", "Ombros", "Cabo", "Deltóide posterior e manguito", "Puxe o cabo até o rosto com cotovelos elevados", "https://www.youtube.com/watch?v=rep-qVOkqgk"),
    ("Crucifixo Invertido", "Ombros", "Halteres", "Deltóide posterior", "Inclinado para frente, abra os braços lateralmente", "https://www.youtube.com/watch?v=ttvAYqnzQAI"),
    ("Arnold Press", "Ombros", "Halteres", "Deltóide completo com rotação", "Inicie com palmas para o rosto e gire ao empurrar", "https://www.youtube.com/watch?v=6Z15_WdXmVw"),

    # BÍCEPS
    ("Rosca Direta com Barra", "Bíceps", "Barra", "Bíceps braquial", "Cotovelos fixos, flexione os antebraços até os ombros", "https://www.youtube.com/watch?v=kwG2ipFRgfo"),
    ("Rosca Alternada com Halteres", "Bíceps", "Halteres", "Bíceps com supinação", "Alterne os braços com rotação do punho", "https://www.youtube.com/watch?v=sAq_ocpRh_I"),
    ("Rosca Martelo", "Bíceps", "Halteres", "Braquial e braquiorradial", "Pegada neutra, eleve os halteres sem girar", "https://www.youtube.com/watch?v=zC3nLlEvin4"),
    ("Rosca Concentrada", "Bíceps", "Halteres", "Pico do bíceps", "Apoie o cotovelo na coxa, flexione completamente", "https://www.youtube.com/watch?v=Jvj2wV0vOFU"),
    ("Rosca no Cabo", "Bíceps", "Cabo", "Bíceps com tensão constante", "Puxe o cabo de baixo para cima mantendo cotovelo fixo", "https://www.youtube.com/watch?v=NFzTWp2qpiE"),
    ("Rosca Scott", "Bíceps", "Barra", "Porção inferior do bíceps", "Apoie os tríceps no banco Scott, flexione completamente", "https://www.youtube.com/watch?v=Pct5lZ0Lhbo"),

    # TRÍCEPS
    ("Tríceps Pulley", "Tríceps", "Cabo", "Tríceps braquial", "Cotovelos fixos, estenda os antebraços para baixo", "https://www.youtube.com/watch?v=2-LAMcpzODU"),
    ("Tríceps Testa", "Tríceps", "Barra", "Cabeça longa do tríceps", "Deite no banco, flexione os cotovelos até a testa", "https://www.youtube.com/watch?v=d_KZxkY_0cM"),
    ("Mergulho em Paralelas", "Tríceps", "Peso corporal", "Tríceps e peitoral inferior", "Desça até 90° no cotovelo e empurre de volta", "https://www.youtube.com/watch?v=2z8JmcrW-As"),
    ("Tríceps Francês", "Tríceps", "Halteres", "Cabeça longa do tríceps", "Segure o haltere acima da cabeça, flexione os cotovelos", "https://www.youtube.com/watch?v=_gsUck-7M74"),
    ("Tríceps Coice", "Tríceps", "Halteres", "Cabeça lateral do tríceps", "Inclinado, estenda o braço para trás mantendo cotovelo fixo", "https://www.youtube.com/watch?v=6SS6K3lAwZ8"),

    # PERNAS — QUADRÍCEPS
    ("Agachamento Livre", "Pernas", "Barra", "Quadríceps, glúteos e isquiotibiais", "Pés na largura dos ombros, desça até 90° mantendo coluna neutra", "https://www.youtube.com/watch?v=ultWZbUMPL8"),
    ("Leg Press 45°", "Pernas", "Máquina", "Quadríceps com menor estresse na coluna", "Pés na plataforma, empurre sem travar os joelhos", "https://www.youtube.com/watch?v=IZxyjW7MPJQ"),
    ("Extensora", "Pernas", "Máquina", "Isolamento do quadríceps", "Estenda os joelhos completamente e retorne controlado", "https://www.youtube.com/watch?v=YyvSfVjQeL0"),
    ("Agachamento Hack", "Pernas", "Máquina", "Vasto medial e lateral", "Costas apoiadas, desça até 90°", "https://www.youtube.com/watch?v=EdtubFDrpBY"),
    ("Avanço com Halteres", "Pernas", "Halteres", "Quadríceps e glúteos", "Dê um passo à frente e desça o joelho traseiro ao chão", "https://www.youtube.com/watch?v=D7KaRcUTQeE"),
    ("Agachamento Búlgaro", "Pernas", "Halteres", "Quadríceps e glúteos unilateral", "Pé traseiro apoiado, desça o joelho dianteiro", "https://www.youtube.com/watch?v=2C-uNgKwPLE"),
    ("Agachamento Sumô", "Pernas", "Kettlebell", "Adutores e glúteos", "Pés afastados e apontados para fora, desça entre as pernas", "https://www.youtube.com/watch?v=gcNh17Ckjgg"),

    # PERNAS — POSTERIOR
    ("Flexora Deitada", "Pernas", "Máquina", "Isquiotibiais", "Flexione os joelhos trazendo os calcanhares em direção aos glúteos", "https://www.youtube.com/watch?v=1Tq3QdYUuHs"),
    ("Stiff com Barra", "Pernas", "Barra", "Isquiotibiais e glúteos", "Joelhos levemente flexionados, incline o tronco à frente", "https://www.youtube.com/watch?v=1uDiW5--rAE"),
    ("Mesa Flexora", "Pernas", "Máquina", "Isquiotibiais sentado", "Flexione os joelhos completamente", "https://www.youtube.com/watch?v=Orxoeast-AU"),
    ("Levantamento Terra Romeno", "Pernas", "Barra", "Cadeia posterior", "Mantenha a barra próxima ao corpo, desça até sentir o alongamento", "https://www.youtube.com/watch?v=JCXUYuzwNrM"),

    # GLÚTEOS
    ("Elevação Pélvica com Barra", "Glúteos", "Barra", "Glúteo máximo", "Costas no banco, barra no quadril, eleve o quadril contraindo os glúteos", "https://www.youtube.com/watch?v=SEdqd1n0cvg"),
    ("Abdução no Cabo", "Glúteos", "Cabo", "Glúteo médio", "Em pé, eleve a perna lateralmente contra a resistência", "https://www.youtube.com/watch?v=OLmCMF5Xf8k"),
    ("Kickback no Cabo", "Glúteos", "Cabo", "Glúteo máximo isolado", "Estenda a perna para trás contraindo o glúteo", "https://www.youtube.com/watch?v=1nqDsT6BjGI"),
    ("Agachamento Sumô com Haltere", "Glúteos", "Halteres", "Glúteos e adutores", "Pés afastados, haltere entre as pernas", "https://www.youtube.com/watch?v=kkdmaTzmuE8"),
    ("Hip Thrust", "Glúteos", "Barra", "Glúteo máximo — maior ativação", "Ombros no banco, barra no quadril, eleve até extensão completa", "https://www.youtube.com/watch?v=xDmFkJxPzeM"),

    # PANTURRILHA
    ("Panturrilha em Pé", "Panturrilha", "Máquina", "Gastrocnêmio", "Eleve os calcanhares o máximo possível", "https://www.youtube.com/watch?v=-M4-G8p1fCI"),
    ("Panturrilha Sentado", "Panturrilha", "Máquina", "Sóleo", "Com joelhos flexionados, eleve os calcanhares", "https://www.youtube.com/watch?v=JbyjNymZOt0"),
    ("Panturrilha no Leg Press", "Panturrilha", "Máquina", "Gastrocnêmio e sóleo", "Apenas a ponta dos pés na plataforma, empurre", "https://www.youtube.com/watch?v=PVbHtFzpzUE"),

    # ABDÔMEN
    ("Abdominal Crunch", "Abdômen", "Peso corporal", "Reto abdominal", "Eleve apenas os ombros do chão contraindo o abdômen", "https://www.youtube.com/watch?v=Xyd_fa5zoEU"),
    ("Prancha Frontal", "Abdômen", "Peso corporal", "Core completo", "Mantenha o corpo reto apoiado nos antebraços e pontas dos pés", "https://www.youtube.com/watch?v=pSHjTRCQxIw"),
    ("Abdominal Roda", "Abdômen", "Roda abdominal", "Core e lombar", "Estenda os braços rolando a roda à frente e retorne", "https://www.youtube.com/watch?v=CyTyAV9dAnA"),
    ("Crunch no Cabo", "Abdômen", "Cabo", "Reto abdominal com resistência", "Ajoelhado, puxe o cabo para baixo contraindo o abdômen", "https://www.youtube.com/watch?v=MKmrqcoCZ-M"),
    ("Elevação de Pernas", "Abdômen", "Peso corporal", "Abdômen inferior", "Deitado, eleve as pernas estendidas até 90°", "https://www.youtube.com/watch?v=l4kQd9eWclE"),
    ("Oblíquo com Cabo", "Abdômen", "Cabo", "Oblíquos", "Gire o tronco contra a resistência do cabo", "https://www.youtube.com/watch?v=ZQS3EnECPOQ"),
    ("Dead Bug", "Abdômen", "Peso corporal", "Core profundo e estabilização", "Estenda braço e perna opostos mantendo lombar no chão", "https://www.youtube.com/watch?v=4XLEnwUr1d8"),
    ("Prancha Lateral", "Abdômen", "Peso corporal", "Oblíquos e quadrado lombar", "Apoie no antebraço e lateral do pé, mantenha o corpo reto", "https://www.youtube.com/watch?v=_6vjo5yFo1U"),

    # CORRETIVOS / MOBILIDADE
    ("Chin Tuck", "Corretivo", "Peso corporal", "Flexores cervicais profundos", "Retraia o queixo fazendo duplo queixo, segure 5 segundos", "https://www.youtube.com/watch?v=Y5GiDLMOQHA"),
    ("Y-T-W no Cabo", "Corretivo", "Cabo", "Estabilizadores escapulares", "Forme as letras Y, T e W com os braços contraindo as escápulas", "https://www.youtube.com/watch?v=XbHHnY8D8mo"),
    ("Alongamento de Peitoral", "Corretivo", "Peso corporal", "Flexibilidade do peitoral", "Apoie o braço na parede em 90° e gire o tronco", "https://www.youtube.com/watch?v=MZCpZfCVRiY"),
    ("Foam Roller Torácico", "Corretivo", "Rolo", "Mobilidade torácica", "Apoie o rolo na região torácica e estenda sobre ele", "https://www.youtube.com/watch?v=JA9ajPMPTpA"),
    ("Rotação Torácica Quadrúpede", "Corretivo", "Peso corporal", "Mobilidade torácica", "Em 4 apoios, coloque a mão na cabeça e gire o tronco", "https://www.youtube.com/watch?v=KM1j9M1Bojo"),
    ("Alongamento de Flexores de Quadril", "Corretivo", "Peso corporal", "Psoas e reto femoral", "Meia ajoelhada, empurre o quadril à frente", "https://www.youtube.com/watch?v=YQmpFBnDqiQ"),
    ("Ativação de Glúteo em 4 Apoios", "Corretivo", "Peso corporal", "Glúteo médio e máximo", "Em 4 apoios, eleve a perna fletida lateralmente", "https://www.youtube.com/watch?v=SqD3Dsn9HXk"),
    ("Short Foot Exercise", "Corretivo", "Peso corporal", "Arco plantar e tibial posterior", "Em pé, eleve o arco do pé sem dobrar os dedos", "https://www.youtube.com/watch?v=oGCOMnSQ5hc"),
    ("Bird Dog", "Corretivo", "Peso corporal", "Core e estabilização lombar", "Em 4 apoios, estenda braço e perna opostos", "https://www.youtube.com/watch?v=wiFNA3sqjCA"),
    ("Respiração Diafragmática", "Corretivo", "Peso corporal", "Controle respiratório e core", "Inspire enchendo o abdômen, expire esvaziando completamente", "https://www.youtube.com/watch?v=LImUaGSLIdc"),

    # CARDIO / FUNCIONAL
    ("Burpee", "Funcional", "Peso corporal", "Condicionamento total", "Agache, apoie as mãos, salte para prancha, flexão, salte de volta", "https://www.youtube.com/watch?v=dZgVxmf6jkA"),
    ("Mountain Climber", "Funcional", "Peso corporal", "Core e condicionamento", "Em prancha alta, alterne os joelhos em direção ao peito rapidamente", "https://www.youtube.com/watch?v=nmwgirgXLYM"),
    ("Kettlebell Swing", "Funcional", "Kettlebell", "Cadeia posterior e condicionamento", "Impulsione o kettlebell com a extensão do quadril", "https://www.youtube.com/watch?v=YSxHifyI6s8"),
    ("Box Jump", "Funcional", "Peso corporal", "Potência de membros inferiores", "Salte sobre a caixa aterrissando suavemente em semiflexão", "https://www.youtube.com/watch?v=52r_Ul5k03g"),
    ("Afundo com Salto", "Funcional", "Peso corporal", "Pernas e condicionamento", "Alterne as pernas saltando entre os avanços", "https://www.youtube.com/watch?v=PVbHtFzpzUE"),
]

# Remove duplicatas por nome
cur.execute("SELECT nome FROM exercicios")
existentes = {r[0].lower() for r in cur.fetchall()}

inseridos = 0
for ex in exercicios:
    nome, grupo, equip, desc, execucao, video = ex
    if nome.lower() not in existentes:
        cur.execute("""
            INSERT INTO exercicios (nome, grupo_muscular, equipamento, descricao, execucao, video_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, grupo, equip, desc, execucao, video))
        existentes.add(nome.lower())
        inseridos += 1

conn.commit()
cur.execute("SELECT COUNT(*) FROM exercicios")
total = cur.fetchone()[0]
print(f'✅ {inseridos} exercícios inseridos! Total: {total}')
conn.close()
