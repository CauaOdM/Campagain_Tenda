import logging

import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import Base, db
import models  # noqa: F401 - registra as tabelas no Base.metadata
import ui


logger = logging.getLogger(__name__)


def initialize_database():
    """Garante que o arquivo atual do SQLite contém todo o schema."""
    with db.begin() as connection:
        Base.metadata.create_all(
            bind=connection,
            checkfirst=True,
        )
        connection.execute(text("SELECT 1"))


try:
    # Não use st.cache_resource aqui: o SQLite local pode ser recriado.
    initialize_database()
except SQLAlchemyError:
    logger.exception("Falha ao inicializar ou validar o banco de dados.")
    st.error(
        "Não foi possível preparar o banco de dados. "
        "Consulte os logs do aplicativo para visualizar o erro completo."
    )
    st.stop()


is_logged_in = bool(getattr(st.user, "is_logged_in", False))

if is_logged_in:
    ui.dashboard()
else:
    ui.login_screen()
