from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from backend.database import get_db, engine
from backend import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Intuitive Care",
    description="API para consulta de despesas de operadoras de saúde",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/operadoras")
def list_operators(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    query = db.query(models.Operadora)

    if search:
        query = query.filter(
            or_(
                models.Operadora.razao_social.ilike(f"%{search}%"),
                models.Operadora.cnpj.ilike(f"%{search}%")
            )
        )

    total = query.count()
    operators = query.offset(skip).limit(limit).all()

    return {
        "data": operators,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/operadoras/{cnpj}")
def get_operator_details(cnpj: str, db: Session = Depends(get_db)):
    operator = db.query(models.Operadora).filter(models.Operadora.cnpj == cnpj).first()

    if not operator:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    return operator

@app.get("/api/operadoras/{cnpj}/despesas")
def get_operator_expenses(cnpj: str, db: Session = Depends(get_db)):
    operator = db.query(models.Operadora).filter(models.Operadora.cnpj == cnpj).first()

    if not operator:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    return operator.despesas

@app.get("/api/estatisticas")
def get_statistics(db: Session = Depends(get_db)):
    data = db.query(
        models.DespesasAgregadas.uf,
        func.sum(models.DespesasAgregadas.total_despesas).label("total")
    ).group_by(models.DespesasAgregadas.uf).order_by(desc("total")).limit(5).all()
    
    resultado = [{"uf": uf, "total": total} for uf, total in data]

    return {
        "por_uf": resultado,
        "mensagem": "Dados recuperados com sucesso"
    }

@app.get("/")
def health_check():
    return {"status": "online", "message": "API rodando com sucesso!"}