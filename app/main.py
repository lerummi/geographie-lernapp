import dotenv
import streamlit as st

from auth import authenticator

state = st.session_state

dotenv.load_dotenv(".env")

st.title("Geographie Lernapp")

authenticator.login()
if state.get("authentication_status", False):
    authenticator.logout(location="main")
    st.write(f"Willkommen *{st.session_state.get("username")}*!")