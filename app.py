import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from PIL import Image
import pandas as pd

# --- Config ---
IMAGES_DIR = Path("images")
NOM_FEUILLE = "image_annotator"  # à créer dans Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

# --- Connexion à Google Sheets ---
def connecter():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open(NOM_FEUILLE).sheet1

# --- Sauvegarde d'une réponse ---
def sauvegarder(sheet, username, image_name, reponse):
    sheet.append_row([username, image_name, reponse, pd.Timestamp.now().isoformat()])

# --- Chargement des images ---
image_files = sorted(IMAGES_DIR.glob("*.[jp][pn]g"))

if not image_files:
    st.error("Aucune image trouvée dans le dossier `images/`.")
    st.stop()

# --- Session state ---
if "index" not in st.session_state:
    st.session_state.index = 0
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Saisie du nom d'utilisateur ---
if not st.session_state.username:
    st.title("🖼️ Annotation d'images")
    name = st.text_input("Entre ton nom d'utilisateur pour commencer :")
    if st.button("Commencer →"):
        if name.strip():
            st.session_state.username = name.strip()
            st.rerun()
        else:
            st.warning("Merci d'entrer un nom d'utilisateur.")
    st.stop()

# --- Connexion Sheet ---
sheet = connecter()

# --- Fin du quiz ---
if st.session_state.index >= len(image_files):
    st.success("✅ Toutes les images ont été annotées !")
    st.stop()

# --- Affichage ---
current_image = image_files[st.session_state.index]

st.title("🖼️ Annotation d'images")
st.progress(st.session_state.index / len(image_files))
st.caption(f"Image {st.session_state.index + 1} / {len(image_files)}")
st.image(Image.open(current_image), width=400)

# --- Formulaire ---
with st.form("annotation_form"):
    response = st.text_input("Qu'est-ce que cette image représente ?", key=f"response_{st.session_state.index}")
    submitted = st.form_submit_button("Valider →")

if submitted:
    if not response.strip():
        st.warning("Merci d'entrer une réponse avant de continuer.")
    else:
        sauvegarder(sheet, st.session_state.username, current_image.name, response.strip())
        st.session_state.index += 1
        st.rerun()