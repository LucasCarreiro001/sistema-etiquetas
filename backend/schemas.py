from pydantic import BaseModel
from datetime import datetime

class ProdutosSchema(BaseModel):
    id: int
    nome: str
    validade_valor: int
    validade_unidade: str
    validade_referencia: str
    armazenamento: str
    categoria: str

    class Config:
        from_attributes = True


class UsuariosSchema(BaseModel):
    id: int
    nome: str
    email: str
    cargo: str

    class Config:
        from_attributes = True

class CriarUsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    cargo: str

class LoginSchema(BaseModel):
    email: str
    senha: str

class CriarProdutosSchemas(BaseModel):
    nome: str
    validade_valor: int
    validade_unidade: str
    validade_referencia: str
    armazenamento: str
    categoria: str

class ValidadeCalculadaSchemas(BaseModel):
    produto_id: int
    nome: str
    manipulado_em: datetime
    validade: datetime
    armazenamento:str

class EtiquetaGerarSchemas(BaseModel):
    produto_id: int
    quantidade: int


class EtiquetaConteudoSchemas(BaseModel):
    produto_nome: str
    manipulado_por: str
    manipulado_em: datetime
    validade: datetime
    armazenamento: str
    quantidade: int

class EtiquetaHistorico(BaseModel):
    id: int
    produto_nome: str
    manipulado_por: str
    manipulado_em: datetime
    validade: datetime
    armazenamento: str
    quantidade: int

    class Config:
        from_attributes = True