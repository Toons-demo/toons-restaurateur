import streamlit as st
import tempfile
import os
import json
from openai import OpenAI

# Configuration de la page
st.set_page_config(page_title="🎙️ Commande vocale Toons", layout="centered")
st.title("🎙️ Assistant vocal Toons")
st.subheader("Parlez, l'IA comprend votre commande")

# Client OpenAI (nouvelle API)
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Enregistrement vocal
st.info("Cliquez ci-dessous pour enregistrer votre commande :")
audio_file = st.file_uploader("🎤 Enregistrez votre commande (format .mp3 ou .wav)", type=["mp3", "wav"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_path = tmp_file.name

    with st.spinner("🧠 Transcription en cours avec Whisper..."):
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        commande_brute = transcript.text

    st.success("Commande reconnue :")
    st.write(f"🗣️ {commande_brute}")

    with st.spinner("🧠 Interprétation par l'IA..."):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """
Tu es un assistant de commande pour un snack rapide. À partir de la phrase utilisateur, extrais et renvoie STRICTEMENT un objet JSON à 5 clés :
- "produit" (string) : ex. "kebab"
- "pain" (string) : ex. "galette"
- "sauces" (array of strings) : ex. ["blanche"]
- "crudites" (array of strings) : ex. ["oignons"] (mettre [] si rien)
- "boisson" (string or null) : ex. "coca" ou null

N’envoie que ce JSON, sans texte additionnel ni mise en forme Markdown.
"""
                },
                {"role": "user", "content": commande_brute}
            ]
        )

        chaine_json = response.choices[0].message.content
        commande_dict = json.loads(chaine_json)

    st.success("✅ Commande formatée :")
    st.json(commande_dict)

    os.remove(tmp_path)
