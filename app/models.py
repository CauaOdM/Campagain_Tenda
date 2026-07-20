from sqlalchemy import Column, String, Integer, DateTime
from database import Base
# Tabela de usuários só mais tarde, não precisa ainda.

# Tabela de marcas

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime)

    def __init__(self, name, created_at):
        self.name = name
        self.created_at = created_at

#Tabela de visão geral
#Tabela de Séries Históricas
