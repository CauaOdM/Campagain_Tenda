import logging

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from database import Base, db
import models  # Import necessário para registrar as tabelas
import ui


logger = logging.getLogger(__name__)


@st.cache_resource(show_spinner=False)
def initialize_database():
    Base.metadata.create_all(
        bind=db,
        checkfirst=True,
    )
    return True


try:
    initialize_database()
except SQLAlchemyError:
    logger.exception("Falha ao inicializar o banco de dados.")

    st.error(
        "Não foi possível inicializar o banco de dados. "
        "Consulte os logs do aplicativo para visualizar o erro completo."
    )
    st.stop()


is_logged_in = bool(
    getattr(st.user, "is_logged_in", False)
)

if is_logged_in:
    ui.dashboard()
else:
    ui.login_screen()