import streamlit as st
from openai import OpenAI
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
import tempfile

# Streamlit page settings
st.set_page_config(page_title="AI VoiceBot", page_icon="🎤")
st.title("🎤 AI VoiceBot Demo")
st.write("Upload a voice message and get an AI response with audio.")

# Initialize OpenAI client (preconfigure your API key in Streamlit secrets)
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")  # Replace with Streamlit secrets for deployment

# Upload voice input
voice_file = st.file_uploader(
    "Upload your voice file (mp3/wav/opus)", 
    type=["mp3", "wav", "opus"]
)

if voice_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(voice_file.read())
        tmp_path = tmp.name

    # Convert .opus files to .wav automatically
    if voice_file.name.endswith(".opus"):
        audio = AudioSegment.from_file(tmp_path, format="opus")
        wav_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(wav_temp.name, format="wav")
        tmp_path = wav_temp.name

    # Play uploaded/convered audio
    st.audio(tmp_path, format="audio/wav")

    # Transcribe audio
    with open(tmp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    user_text = transcription.text
    st.text_area("You said:", value=user_text, height=100)

    # Generate AI response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_text}],
        max_tokens=200
    )
    bot_text = response.choices[0].message.content
    st.text_area("AI Response:", value=bot_text, height=100)

    # Convert AI response to audio
    tts = gTTS(bot_text)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    st.audio(audio_bytes.getvalue(), format="audio/mp3")
