from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    # Coluna de chave primária
    usuario: Mapped[str] = mapped_column(primary_key=True)
    
    # Colunas obrigatórias
    email: Mapped[str] = mapped_column(nullable=False, unique=True) #pra evitar emails duplicados
    tipo_usuario: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    
    # Coluna opcional (nullable)
    recovery_token: Mapped[str] = mapped_column(nullable=True)


