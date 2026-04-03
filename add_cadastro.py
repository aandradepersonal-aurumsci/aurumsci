with open('app/routers/portal_aluno.py', 'r') as f:
    c = f.read()

novo = """

class CadastroRapido(BaseModel):
    nome: str
    email: str
    senha: str

@router.post("/cadastro")
def cadastro_rapido(dados: CadastroRapido, db: Session = Depends(get_db)):
    from app.models import Aluno
    existente = db.query(Aluno).filter(Aluno.email == dados.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")
    aluno = Aluno(
        nome=dados.nome, email=dados.email,
        telefone="", objetivo="hipertrofia",
        nivel_experiencia="iniciante", sexo="nao_informado",
        personal_id=1
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    cred = AlunoCredencial(aluno_id=aluno.id, email=dados.email, senha_hash=pwd_context.hash(dados.senha))
    db.add(cred)
    db.commit()
    return {"aluno_id": aluno.id, "mensagem": "Conta criada com sucesso!"}
"""

with open('app/routers/portal_aluno.py', 'w') as f:
    f.write(c + novo)
print('OK!')
