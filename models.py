from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'users'
    usuario:Mapped[str] = mapped_column(primary_key = True)
    email:Mapped[str]
    tipo_usuario:Mapped[str]
    password:Mapped[str]