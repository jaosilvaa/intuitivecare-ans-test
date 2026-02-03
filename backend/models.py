from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship
from backend.database import Base

class Operadora(Base):
    __tablename__ = "operadoras"

    registro_ans = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String)
    razao_social = Column(String)
    modalidade = Column(String)
    uf = Column(String)

    despesas = relationship("DemonstracaoContabil", back_populates="operadora")

class DemonstracaoContabil(Base):
    __tablename__ = "demonstracoes_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    registro_ans = Column(Integer, ForeignKey("operadoras.registro_ans"))
    ano = Column(Integer)
    trimestre = Column(Integer)
    valor_despesa = Column(Numeric(18, 2))

    operadora = relationship("Operadora", back_populates="despesas")

class DespesasAgregadas(Base):
    __tablename__= "despesas_agregadas"
    registro_ans = Column(Integer, primary_key=True)
    razao_social = Column(String)
    uf = Column(String)
    total_despesas = Column(Numeric(18, 2))
    media_trimestral = Column(Numeric(18, 2))
    desvio_padrao = Column(Numeric(18, 2))
