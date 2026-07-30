from pydantic import BaseModel

class ProdutosSchema(BaseModel):
    id: int
    nome: str
    validade_valor: int
    validade_unidade: str
    validade_referencia: str
    armazenamento: str

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
