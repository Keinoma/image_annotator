import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

# --- Config ---
IMAGES_DIR = Path("images")
RESPONSES_FILE = Path("responses.csv")

# --- Chargement des images ---
image_files = sorted(IMAGES_DIR.glob("*.[jp][pn]g"))  # .jpg et .png

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

# --- Fin du quiz ---
if st.session_state.index >= len(image_files):
    st.success("✅ Toutes les images ont été annotées !")
    if RESPONSES_FILE.exists():
        df = pd.read_csv(RESPONSES_FILE)
        st.dataframe(df)
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
        # Sauvegarde dans le CSV
        new_row = pd.DataFrame([{
            "username": st.session_state.username,
            "image": current_image.name,
            "reponse": response.strip(),
            "timestamp": pd.Timestamp.now().isoformat()
        }])
        if RESPONSES_FILE.exists():
            new_row.to_csv(RESPONSES_FILE, mode="a", header=False, index=False)
        else:
            new_row.to_csv(RESPONSES_FILE, index=False)

        st.session_state.index += 1
        st.rerun()