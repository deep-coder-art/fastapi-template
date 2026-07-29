from sqlmodel import Session, SQLModel, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

_connect_args = (
    {"check_same_thread": False}
    if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite")
    else {}
)
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), connect_args=_connect_args
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Postgres: tables come from Alembic migrations.
    # SQLite: create tables from models (Alembic history is Postgres-specific).
    if settings.SQLITE_DB:
        SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
