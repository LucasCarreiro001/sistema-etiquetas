from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Produtos, Usuarios, Etiquetas
from typing import List, Optional
from pydantic import BaseModel
from schemas import ProdutosSchema, UsuariosSchema, LoginSchema, ValidadeCalculadaSchemas, EtiquetaConteudoSchemas, EtiquetaGerarSchemas
from typing import List
from schemas import CriarUsuarioSchema, CriarProdutosSchemas, EtiquetaHistorico
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, date
from calculo_validade import calcular_validade
from auth import hash_password, criar_token, verify_password, usuario_atual, exigir_cargo_admin
from fastapi.middleware.cors import CORSMiddleware



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
    return db.query(Produtos).filter(Produtos.ativo == True).all()

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

@app.post('/produtos', response_model=CriarProdutosSchemas)
def criar_produto(dados: CriarProdutosSchemas, db:Session=Depends(get_db), usuario: dict = Depends(exigir_cargo_admin)):
    novo_produto = Produtos(
        nome = dados.nome,
        validade_valor= dados.validade_valor,
        validade_unidade=dados.validade_unidade,
        validade_referencia = dados.validade_referencia,
        armazenamento = dados.armazenamento,
        categoria = dados.categoria
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return(novo_produto)

@app.get('/produtos/buscar', response_model=list[ProdutosSchema])
def buscar_produtos(nome:str, db: Session = Depends(get_db), usuario: dict = Depends(usuario_atual)):
    return db.query(Produtos).filter(Produtos.ativo == True, Produtos.nome.ilike(f"%{nome}%")).all()

@app.put('/produtos/{produto_id}', response_model=ProdutosSchema)
def editar(produto_id: int, dados: CriarProdutosSchemas, db: Session =Depends(get_db), usuario:dict=Depends(exigir_cargo_admin)):
    produto = db.query(Produtos).filter(Produtos.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="produto não encontrado")
    produtos = Produtos(
    nome = dados.nome,
    validade_valor = dados.validade_valor,
    validade_unidade = dados.validade_unidade,
    validade_referencia = dados.validade_referencia,
    armazenamento = dados.armazenamento,
    categoria = dados.categoria)

    db.commit()
    db.refresh(produtos)
    return produtos

@app.delete('/produtos/{produto_id}')
def desativar_produto(produto_id: int, db: Session= Depends(get_db), usuario: dict = Depends(exigir_cargo_admin)):
    produto = db.query(Produtos).filter(Produtos.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail='Produto não encontrado')

    produto.ativo = False
    db.commit()
    return {'mensagem': f'{produto.nome} desativado com sucesso'}

@app.get("/produtos/{produto_id}/validade", response_model=ValidadeCalculadaSchemas)
def consultar_validade(produto_id: int, db: Session = Depends(get_db), usuario: dict = Depends(usuario_atual)):
    produto = db.query(Produtos).filter(Produtos.id == produto_id, Produtos.ativo == True).first()
    if not produto:
        raise HTTPException(status_code=404, detail='Produto não encontrado')

    agora = datetime.now()
    validade = calcular_validade(produto, agora)

    return ValidadeCalculadaSchemas(
        produto_id=produto.id,
        nome=produto.nome,
        manipulado_em=agora,
        validade=validade,
        armazenamento=produto.armazenamento
    )

@app.post('/etiquetas/gerar', response_model=EtiquetaConteudoSchemas)
def criar_etiquetas(dados: EtiquetaGerarSchemas, db: Session = Depends(get_db), usuario: dict = Depends(usuario_atual)):
    produto = db.query(Produtos).filter(Produtos.id == dados.produto_id, Produtos.ativo == True).first()

    if not produto:
        raise HTTPException(status_code=404, detail='Produto não encontrado')

    usuario_logado = db.query(Usuarios).filter(Usuarios.id == usuario['user_id']).first()

    agora = datetime.now()
    validade = calcular_validade(produto, agora)

    nova_etiqueta = Etiquetas(
        produto_id=produto.id,
        user_id=usuario_logado.id,
        data_hora_criacao=agora,
        data_hora_validade = validade,
        armazenamento = produto.armazenamento,
        qnt_etiquetas = dados.quantidade
    )
    db.add(nova_etiqueta)
    db.commit()

    return EtiquetaConteudoSchemas(
        produto_nome=produto.nome,
        manipulado_por=usuario_logado.nome,
        manipulado_em=agora,
        validade=validade,
        armazenamento=produto.armazenamento,
        quantidade=dados.quantidade
    )



@app.get("/etiquetas", response_model=List[EtiquetaHistorico])
def listar_historico(
    produto_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(usuario_atual)
):
    query = db.query(Etiquetas)

    if produto_id is not None:
        query = query.filter(Etiquetas.produto_id == produto_id)

    if data_inicio is not None:
        query = query.filter(Etiquetas.data_hora_criacao >= data_inicio)

    if data_fim is not None:
        query = query.filter(Etiquetas.data_hora_criacao <= data_fim)

    etiquetas = query.order_by(Etiquetas.data_hora_criacao.desc()).all()

    resultado = []
    for e in etiquetas:
        resultado.append(EtiquetaHistorico(
            id=e.id,
            produto_nome=e.produto.nome,
            manipulado_por=e.usuario.nome,
            manipulado_em=e.data_hora_criacao,
            validade=e.data_hora_validade,
            armazenamento=e.armazenamento,
            quantidade=e.qnt_etiquetas
        ))

    return resultado

@app.get('/produtos/categoria/{categoria}', response_model= List[ProdutosSchema])
def categoria_produtos(categoria:str, db: Session = Depends(get_db), usuario:dict = Depends(usuario_atual)):
    return db.query(Produtos).filter(Produtos.categoria == categoria, Produtos.ativo == True).all( )