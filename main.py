from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Produtos, Usuarios
from typing import List
from pydantic import BaseModel
from schemas import ProdutosSchema, UsuariosSchema, LoginSchema
from typing import List
from schemas import CriarUsuarioSchema
from auth import hash_password, criar_token, verify_password


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def raiz():
    return {"message": "API de Impressão de Etiquetas"}

@app.get("/produtos",  response_model=List[ProdutosSchema])
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produtos).all()
    return produtos


@app.get("/usuarios", response_model=List[UsuariosSchema])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuarios).all()

@app.post('/usuarios', response_model=UsuariosSchema)
def criar_usuario(dados_usuario: CriarUsuarioSchema, db: Session = Depends(get_db)):
    novo_usuario  = Usuarios(
        nome=dados_usuario.nome,
        email=dados_usuario.email,
        senha_hash=hash_password(dados_usuario.senha),
        cargo=dados_usuario.cargo
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@app.post('/login')
def login(dados_login: LoginSchema, db: Session = Depends(get_db)):
    usuario = db.query(Usuarios).filter(Usuarios.email == dados_login.email).first()

    if not usuario or not verify_password(dados_login.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token({'user_id': usuario.id, 'cargo': usuario.cargo})
    return {'acesso_token': token, 'token_type': 'bearer'}