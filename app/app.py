import streamlit as st

from database import db, Base
import models
import ui

Base.metadata.create_all(bind=db)

is_logged_in = getattr(st.user, "is_logged_in", False)

if not is_logged_in:
    ui.login_screen()
else:
    ui.dashboard()