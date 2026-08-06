from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Produtos, Usuarios
from typing import List
from pydantic import BaseModel
from schemas import ProdutosSchema, UsuariosSchema, LoginSchema
from typing import List
from schemas import CriarUsuarioSchema
from fastapi.security import OAuth2PasswordRequestForm
from auth import hash_password, criar_token, verify_password, usuario_atual, exigir_cargo_admin


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

@app.get("/produtos", response_model=List[ProdutosSchema])
def listar_produtos(db: Session = Depends(get_db), usuario: dict = Depends(usuario_atual)):
    produtos = db.query(Produtos).all()
    return produtos

@app.get("/usuarios", response_model=List[UsuariosSchema])
def listar_usuarios(db: Session = Depends(get_db), usuario: dict = Depends(exigir_cargo_admin)):
    return db.query(Usuarios).all()

@app.post("/login")
def login(
    dados_login: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuarios).filter(
        Usuarios.email == dados_login.username
    ).first()

    if not usuario or not verify_password(
        dados_login.password,
        str(usuario.senha_hash)
    ):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token({
        "user_id": usuario.id,
        "cargo": usuario.cargo
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.post('/usuarios', response_model=UsuariosSchema)
def criar_usuario(dados: CriarUsuarioSchema, db: Session = Depends(get_db), usuario: dict = Depends(exigir_cargo_admin)):
    novo_usuario = Usuarios(
        nome = dados.nome,
        email = dados.email,
        senha_hash = hash_password(dados.senha),
        cargo = dados.cargo
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return(novo_usuario)