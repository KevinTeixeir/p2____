import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ecommerce_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo ORM
class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

# Schemas de Validação
class ProdutoBase(BaseModel):
    nome: str
    preco: float
    estoque: int = 0
    ativo: bool = True

    @field_validator('nome')
    def nome_nao_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError('O nome do produto não pode ser vazio')
        return v

    @field_validator('preco')
    def preco_maior_que_zero(cls, v):
        if v <= 0:
            raise ValueError('O preço deve ser maior que zero')
        return v

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int

    class Config:
        from_attributes = True

app = FastAPI(title="E-commerce Product API")

# Cria as tabelas na inicialização local
Base.metadata.create_all(bind=engine)

# Endpoints Obrigatórios
@app.get("/produtos", response_model=List[ProdutoResponse], status_code=status.HTTP_200_OK)
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()

@app.post("/produtos", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.get("/produtos/{produto_id}", response_model=ProdutoResponse, status_code=status.HTTP_200_OK)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto

@app.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    return None
