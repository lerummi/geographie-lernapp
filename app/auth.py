import dotenv
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

dotenv.load_dotenv(".env")

st.title("Geographie Lernapp")

config = st.secrets.to_dict()

stauth.Hasher.hash_passwords(config["credentials"])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
