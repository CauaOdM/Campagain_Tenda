from sqlalchemy import Column, Date, DateTime, Float, Integer, String, func

from database import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class CampaignResult(Base):
    __tablename__ = "campaign_results"

    id = Column(Integer, primary_key=True)
    brand_name = Column(String, nullable=False, index=True)
    report_month = Column(Date, nullable=False, index=True)
    campaign = Column(String, nullable=False, index=True)
    qtd_venda = Column(Integer, default=0)
    disparados = Column(Integer, default=0)
    entregues = Column(Integer, default=0)
    taxa_entrega = Column(Float, default=0.0)
    aberturas = Column(Integer, default=0)
    cliques = Column(Integer, default=0)
    clientes = Column(Integer, default=0)
    receita = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class CompositionResult(Base):
    __tablename__ = "composition_results"

    id = Column(Integer, primary_key=True)
    brand_name = Column(String, nullable=False, index=True)
    report_month = Column(Date, nullable=False, index=True)
    categoria = Column(String, nullable=False, index=True)
    comprador = Column(String, nullable=False)
    contato = Column(String, nullable=False)
    receita = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    taxa_desconto = Column(Float, default=0.0)
    participacao_receita = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
