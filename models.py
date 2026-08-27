from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cargo = Column(String(50), nullable=False)

    __table_args__ = (
        CheckConstraint("cargo IN ('funcionario', 'admin')", name="check_cargo"),
    )

class Produtos(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    validade_valor = Column(Integer, nullable=False)
    validade_unidade = Column(String(10), nullable=False)
    validade_referencia = Column(String(10), nullable=False)
    armazenamento = Column(String(50), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    categoria = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "validade_unidade IN ('horas', 'dias')",
            name="check_unidade_valida"
        ),
        CheckConstraint(
            "validade_referencia IN ('padrao', 'fim_do_dia')",
            name="check_regra_valida"
        ),
        CheckConstraint(
            "armazenamento IN ('congelado', 'refrigerado', 'temperatura ambiente')",
            name="check_condicao_valida"
        ),

        CheckConstraint(
            "categoria IN ('padaria', 'confeitaria', 'bebidas', 'comidas', 'sobremesas')",
            name='check_categoria_valida'
        )
    )

class Etiquetas(Base):
    __tablename__ = "etiquetas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_hora_criacao = Column(DateTime, nullable=False)
    data_hora_validade = Column(DateTime, nullable=False)
    armazenamento = Column(String(50), nullable=False)
    qnt_etiquetas = Column(Integer, nullable=False)

    produto = relationship("Produtos")
    usuario = relationship("Usuarios")

