import psycopg2
conn = psycopg2.connect('postgresql://postgres:TvlbrPuVPWsIFQWykuYnAwEVBtkmYlmF@hopper.proxy.rlwy.net:25197/railway')
cur = conn.cursor()

cur.execute("SELECT nome FROM exercicios")
existentes = {r[0].lower() for r in cur.fetchall()}

novos = [
    # ABDÔMEN
    ("Prancha Frontal", "Abdômen", "Peso Corporal", "Core completo", "https://www.youtube.com/watch?v=pSHjTRCQxIw"),
    ("Crunch no Cabo", "Abdômen", "Cabo", "Reto abdominal com resistência", "https://www.youtube.com/watch?v=MKmrqcoCZ-M"),
    ("Elevação de Pernas", "Abdômen", "Peso Corporal", "Abdômen inferior", "https://www.youtube.com/watch?v=l4kQd9eWclE"),
    ("Oblíquo no Cabo", "Abdômen", "Cabo", "Oblíquos", "https://www.youtube.com/watch?v=ZQS3EnECPOQ"),
    ("Dead Bug", "Abdômen", "Peso Corporal", "Core profundo", "https://www.youtube.com/watch?v=4XLEnwUr1d8"),
    ("Prancha Lateral", "Abdômen", "Peso Corporal", "Oblíquos", "https://www.youtube.com/watch?v=_6vjo5yFo1U"),
    ("Roda Abdominal", "Abdômen", "Roda", "Core e lombar", "https://www.youtube.com/watch?v=CyTyAV9dAnA"),
    # BÍCEPS
    ("Rosca Scott", "Bíceps", "Barra", "Porção inferior do bíceps", "https://www.youtube.com/watch?v=Pct5lZ0Lhbo"),
    ("Rosca Concentrada", "Bíceps", "Halteres", "Pico do bíceps", "https://www.youtube.com/watch?v=Jvj2wV0vOFU"),
    ("Rosca no Cabo", "Bíceps", "Cabo", "Tensão constante", "https://www.youtube.com/watch?v=NFzTWp2qpiE"),
    # TRÍCEPS
    ("Tríceps Francês", "Tríceps", "Halteres", "Cabeça longa", "https://www.youtube.com/watch?v=_gsUck-7M74"),
    ("Tríceps Coice", "Tríceps", "Halteres", "Cabeça lateral", "https://www.youtube.com/watch?v=6SS6K3lAwZ8"),
    ("Mergulho em Paralelas", "Tríceps", "Peso Corporal", "Tríceps e peitoral", "https://www.youtube.com/watch?v=2z8JmcrW-As"),
    # PEITO
    ("Peck Deck", "Peito", "Máquina", "Isolamento do peitoral", "https://www.youtube.com/watch?v=Z57CtFmRMxA"),
    ("Supino Declinado com Barra", "Peito", "Barra", "Peitoral inferior", "https://www.youtube.com/watch?v=LfyQBUKR8SE"),
    ("Supino Inclinado com Barra", "Peito", "Barra", "Peitoral superior", "https://www.youtube.com/watch?v=DbFgADa2PL8"),
    ("Crossover no Cabo Alto", "Peito", "Cabo", "Peitoral inferior", "https://www.youtube.com/watch?v=taI4XduLpTk"),
    # GLÚTEOS
    ("Hip Thrust com Barra", "Glúteos", "Barra", "Glúteo máximo", "https://www.youtube.com/watch?v=xDmFkJxPzeM"),
    ("Elevação Pélvica", "Glúteos", "Peso Corporal", "Glúteo máximo", "https://www.youtube.com/watch?v=SEdqd1n0cvg"),
    ("Abdução no Cabo", "Glúteos", "Cabo", "Glúteo médio", "https://www.youtube.com/watch?v=OLmCMF5Xf8k"),
    ("Kickback no Cabo", "Glúteos", "Cabo", "Glúteo máximo isolado", "https://www.youtube.com/watch?v=1nqDsT6BjGI"),
    ("Agachamento Sumô", "Glúteos", "Halteres", "Glúteos e adutores", "https://www.youtube.com/watch?v=gcNh17Ckjgg"),
    # PANTURRILHA
    ("Panturrilha em Pé na Máquina", "Panturrilha", "Máquina", "Gastrocnêmio", "https://www.youtube.com/watch?v=-M4-G8p1fCI"),
    ("Panturrilha Sentado", "Panturrilha", "Máquina", "Sóleo", "https://www.youtube.com/watch?v=JbyjNymZOt0"),
    ("Panturrilha no Leg Press", "Panturrilha", "Máquina", "Gastrocnêmio e sóleo", "https://www.youtube.com/watch?v=PVbHtFzpzUE"),
    # OMBROS
    ("Arnold Press", "Ombros", "Halteres", "Deltóide completo", "https://www.youtube.com/watch?v=6Z15_WdXmVw"),
    ("Crucifixo Invertido", "Ombros", "Halteres", "Deltóide posterior", "https://www.youtube.com/watch?v=ttvAYqnzQAI"),
    ("Desenvolvimento com Barra", "Ombros", "Barra", "Deltóide completo", "https://www.youtube.com/watch?v=2yjwXTZQDDI"),
    # COSTAS
    ("Levantamento Terra", "Costas", "Barra", "Cadeia posterior completa", "https://www.youtube.com/watch?v=op9kVnSso6Q"),
    ("Puxada Supinada", "Costas", "Cabo", "Bíceps e latíssimo", "https://www.youtube.com/watch?v=rT7FtaLZD48"),
    ("Remada Alta", "Costas", "Barra", "Trapézio e romboides", "https://www.youtube.com/watch?v=NN_T8jmZNmQ"),
    ("Puxada no Cabo Reto", "Costas", "Cabo", "Latíssimo inferior", "https://www.youtube.com/watch?v=wVTnFxFBUEI"),
    # PERNAS
    ("Agachamento Búlgaro", "Pernas", "Halteres", "Quadríceps unilateral", "https://www.youtube.com/watch?v=2C-uNgKwPLE"),
    ("Avanço com Halteres", "Pernas", "Halteres", "Quadríceps e glúteos", "https://www.youtube.com/watch?v=D7KaRcUTQeE"),
    ("Levantamento Terra Romeno", "Pernas", "Barra", "Isquiotibiais", "https://www.youtube.com/watch?v=JCXUYuzwNrM"),
    ("Mesa Flexora", "Pernas", "Máquina", "Isquiotibiais sentado", "https://www.youtube.com/watch?v=Orxoeast-AU"),
    ("Hack Squat", "Pernas", "Máquina", "Vasto medial e lateral", "https://www.youtube.com/watch?v=EdtubFDrpBY"),
    # CROSSFIT / FUNCIONAL
    ("Thruster", "Funcional", "Barra", "Full body — agachamento + desenvolvimento", "https://www.youtube.com/watch?v=L219ltL15zk"),
    ("Clean and Jerk", "Funcional", "Barra", "Arrancada e arremesso olímpico", "https://www.youtube.com/watch?v=iVLDn0-K0oE"),
    ("Snatch", "Funcional", "Barra", "Arrancada olímpica", "https://www.youtube.com/watch?v=9xQp2sldyts"),
    ("Dumbbell Snatch", "Funcional", "Halteres", "Arrancada unilateral com haltere", "https://www.youtube.com/watch?v=eFfmkMpGhKE"),
    ("Box Jump", "Funcional", "Peso Corporal", "Potência de membros inferiores", "https://www.youtube.com/watch?v=52r_Ul5k03g"),
    ("Walking Lunge", "Funcional", "Halteres", "Avanço caminhando — pernas e glúteos", "https://www.youtube.com/watch?v=L8fvypPrzzs"),
    ("Front Squat", "Funcional", "Barra", "Agachamento frontal — quadríceps e core", "https://www.youtube.com/watch?v=m4ytaCJZpl0"),
    ("Back Squat", "Funcional", "Barra", "Agachamento traseiro — força total", "https://www.youtube.com/watch?v=ultWZbUMPL8"),
    ("Step Up", "Funcional", "Halteres", "Subida em banco — pernas e glúteos", "https://www.youtube.com/watch?v=dQqApCGd5Ss"),
    ("Burpee", "Funcional", "Peso Corporal", "Condicionamento total", "https://www.youtube.com/watch?v=dZgVxmf6jkA"),
    ("Kettlebell Swing", "Funcional", "Kettlebell", "Cadeia posterior e condicionamento", "https://www.youtube.com/watch?v=YSxHifyI6s8"),
    ("Mountain Climber", "Funcional", "Peso Corporal", "Core e condicionamento", "https://www.youtube.com/watch?v=nmwgirgXLYM"),
    ("Pull Up", "Funcional", "Peso Corporal", "Barra fixa pronada — costas e bíceps", "https://www.youtube.com/watch?v=eGo4IYlbE5g"),
    ("Push Press", "Funcional", "Barra", "Desenvolvimento com impulso de pernas", "https://www.youtube.com/watch?v=X6-DMh-t4nQ"),
    ("Deadlift Sumo", "Funcional", "Barra", "Terra sumo — adutores e posterior", "https://www.youtube.com/watch?v=gcNh17Ckjgg"),
    ("Rope Climb", "Funcional", "Corda", "Escalada de corda — costas e bíceps", "https://www.youtube.com/watch?v=nTEjGqbRHlE"),
    ("Double Under", "Funcional", "Corda", "Pular corda dupla — condicionamento", "https://www.youtube.com/watch?v=fkELU7F7FaM"),
    ("Toes to Bar", "Funcional", "Barra", "Abdômen na barra — core", "https://www.youtube.com/watch?v=1S9kemPOzgw"),
    ("Rowing Machine", "Funcional", "Máquina", "Remada ergométrica — full body cardio", "https://www.youtube.com/watch?v=H0r_ZPXJLtg"),
    ("Assault Bike", "Funcional", "Máquina", "Bicicleta assault — condicionamento total", "https://www.youtube.com/watch?v=7kgZnJGDPQY"),
    # AVALIAÇÃO
    ("Dinamômetro — Preensão Manual", "Avaliação", "Dinamômetro", "Teste de força de preensão manual. Bohannon (2019) JAMA.", "https://www.youtube.com/watch?v=LqXZ628YFj0"),
]

inseridos = 0
for nome, grupo, equip, desc, video in novos:
    if nome.lower() not in existentes:
        cur.execute("""
            INSERT INTO exercicios (nome, grupo_muscular, equipamento, descricao, video_url)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, grupo, equip, desc, video))
        existentes.add(nome.lower())
        inseridos += 1

conn.commit()
cur.execute('SELECT COUNT(*) FROM exercicios')
print(f'Inseridos: {inseridos} | Total: {cur.fetchone()[0]}')
conn.close()
