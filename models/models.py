from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class SecretsOrm(Base):
    __tablename__ = "secrets"

    id: Mapped[int] = mapped_column(primary_key=True)
    secret_data: Mapped[str]
    hashed_password: Mapped[str | None]
    is_viewed: Mapped[bool] = mapped_column(default=False)
    secret_id: Mapped[str | None] = mapped_column(unique=True, nullable=True)



