import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ── Configuração do Banco ──────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dimdim:dimdim123@db-dimdim:5432/dimdimdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── Modelo ORM ─────────────────────────────────────────────────────────────────
class Conta(Base):
    __tablename__ = "contas"

    id          = Column(Integer, primary_key=True, index=True)
    titular     = Column(String(100), nullable=False)
    cpf         = Column(String(14), unique=True, nullable=False)
    saldo       = Column(Float, default=0.0)
    tipo        = Column(String(20), default="corrente")  # corrente ou poupança
    criado_em   = Column(DateTime, default=datetime.utcnow)

# Cria tabela automaticamente ao iniciar
Base.metadata.create_all(bind=engine)

# ── Schemas Pydantic ───────────────────────────────────────────────────────────
class ContaCreate(BaseModel):
    titular: str
    cpf: str
    saldo: float = 0.0
    tipo: str = "corrente"

class ContaUpdate(BaseModel):
    titular: Optional[str] = None
    saldo: Optional[float] = None
    tipo: Optional[str] = None

class ContaResponse(BaseModel):
    id: int
    titular: str
    cpf: str
    saldo: float
    tipo: str
    criado_em: datetime

    class Config:
        from_attributes = True

# ── Dependency ─────────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DimDim API",
    description="API RESTful - Instituição Financeira DimDim | FIAP DevOps CP3",
    version="1.0.0"
)

# ── Rotas CRUD ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "DimDim API está no ar!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy", "app": "DimDimApp", "version": "1.0.0"}

# CREATE
@app.post("/contas", response_model=ContaResponse, status_code=201)
def criar_conta(conta: ContaCreate, db: Session = Depends(get_db)):
    existente = db.query(Conta).filter(Conta.cpf == conta.cpf).first()
    if existente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    nova = Conta(**conta.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

# READ ALL
@app.get("/contas", response_model=list[ContaResponse])
def listar_contas(db: Session = Depends(get_db)):
    return db.query(Conta).all()

# READ ONE
@app.get("/contas/{conta_id}", response_model=ContaResponse)
def buscar_conta(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(Conta).filter(Conta.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return conta

# UPDATE
@app.put("/contas/{conta_id}", response_model=ContaResponse)
def atualizar_conta(conta_id: int, dados: ContaUpdate, db: Session = Depends(get_db)):
    conta = db.query(Conta).filter(Conta.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(conta, campo, valor)
    db.commit()
    db.refresh(conta)
    return conta

# DELETE
@app.delete("/contas/{conta_id}", status_code=204)
def deletar_conta(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(Conta).filter(Conta.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    db.delete(conta)
    db.commit()
    return None
