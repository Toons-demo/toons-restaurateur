import streamlit as st
import openai
import tempfile
import os

st.set_page_config(page_title="🎙️ Commande vocale Toons", layout="centered")
st.title("🎙️ Assistant vocal Toons")
st.subheader("Parlez, l'IA comprend votre commande")

# Clé API OpenAI (tu dois la définir dans ton environnement Streamlit Cloud)
openai.api_key = st.secrets["openai_api_key"]

# Enregistrement vocal
st.info("Cliquez ci-dessous pour enregistrer votre commande :")
audio_file = st.file_uploader("🎤 Enregistrez votre commande (format .mp3 ou .wav)", type=["mp3", "wav"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_path = tmp_file.name

    with st.spinner("🧠 Transcription en cours avec Whisper..."):
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=open(tmp_path, "rb")
        )
        commande_brute = transcript["text"]

    st.success("Commande reconnue :")
    st.write(f"🗣️ {commande_brute}")

    with st.spinner("🧠 Interprétation par l'IA..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un assistant de commande pour un snack. Tu dois structurer clairement la commande pour qu'elle soit transmise au restaurateur. N'invente rien."},
                {"role": "user", "content": commande_brute}
            ]
        )
        commande_formatee = response.choices[0].message.content

    st.success("Commande formatée à envoyer :")
    st.markdown(f"""
    ```
    {commande_formatee}
    ```
    """)

    # Plus tard : envoyer via API ou base partagée
    # st.button("📤 Envoyer au restaurateur")

    os.remove(tmp_path)
