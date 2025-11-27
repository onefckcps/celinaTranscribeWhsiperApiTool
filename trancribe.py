import streamlit as st
import os
from openai import OpenAI
from pydub import AudioSegment
import io

# Konfiguration
CHUNK_SIZE_MB = 24  # Puffer unter 25MB Limit halten
TEMP_FOLDER = "temp_chunks"

st.set_page_config(page_title="Celina Transkribierer", layout="centered")
st.title("🎙️ Celinas Interview Transkribierer!")
st.markdown("Hier du Spinne - einfach die Audio-Datei von dem Interview hochladen und dann auf Transkribieren klicken. :) PEEEENIS 8=====> LOL. Achso und dann musst du in das Textfeld unterhalb den Key der in unserem Chat markiert ist eingeben! (ohne wirds nicht funktionieren). Bitte den API KeyNICHT an Freunde oder andere weitergeben, weil das KOSTET MICH GELD!")
st.markdown("")

# 1. API Key Input
api_key = st.text_input("OpenAI API Key", type="password")

# 2. File Uploader
uploaded_file = st.file_uploader("Interview Audio-Datei wählen (mp3, wav, m4a...)", type=["mp3", "wav", "m4a", "mp4"])

def transcribe_chunk(client, file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text"
        )
    return transcript

if st.button("Transkribieren starten") and uploaded_file and api_key:
    client = OpenAI(api_key=api_key)
    st.info("Verarbeite Audio...")
    
    # Ordner für Chunks erstellen
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)

    # Datei laden
    audio = AudioSegment.from_file(uploaded_file)
    
    # Prüfen ob Splitting nötig ist (Grobe Schätzung: 1 Min MP3 ~ 1 MB, aber wir gehen nach Länge)
    # Sicherer Ansatz: 10 Minuten Chunks (Whisper Kontext ist eh begrenzt)
    ten_minutes = 10 * 60 * 1000
    chunks = [audio[i:i + ten_minutes] for i in range(0, len(audio), ten_minutes)]
    
    full_transcript = ""
    progress_bar = st.progress(0)
    
    for i, chunk in enumerate(chunks):
        chunk_name = os.path.join(TEMP_FOLDER, f"chunk_{i}.mp3")
        chunk.export(chunk_name, format="mp3")
        
        st.write(f"Sende Teil {i+1} von {len(chunks)} an API...")
        text = transcribe_chunk(client, chunk_name)
        full_transcript += text + " "
        
        # Aufräumen
        os.remove(chunk_name)
        progress_bar.progress((i + 1) / len(chunks))

    st.success("Fertig!")
    st.text_area("Ergebnis:", value=full_transcript, height=300)
    
    # Download Button
    st.download_button("Transkript herunterladen", full_transcript, file_name="transkript.txt")
    
    # Temp Ordner löschen
    os.rmdir(TEMP_FOLDER)

elif not api_key:
    st.warning("Bitte API Key eingeben.")