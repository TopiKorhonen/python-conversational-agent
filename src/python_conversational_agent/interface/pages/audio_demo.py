import streamlit as st
import hashlib
import torch
from src.python_conversational_agent.speech.app import AudioProcessor

st.set_page_config(page_title="Voice Pipeline", layout="centered")
st.title("Whisper → Piper Pipeline")

cuda = torch.cuda.is_available()
if cuda:
    st.sidebar.success("CUDA")
else:
    st.sidebar.error("CPU")

whisper_model = st.sidebar.selectbox("Whisper Model", ["tiny", "base", "small", "medium", "large-v3"], index=1)
compute_type = st.sidebar.selectbox("Compute", ["float16", "int8", "int8_float16"], index=0 if cuda else 1)
piper_voice = st.sidebar.selectbox("Piper Voice", ["en_US-amy-medium", "fi_FI-harri-low", "en_US-lessac-medium", "fi_FI-harri-medium"], index=0)

@st.cache_resource(show_spinner="Loading Models...", max_entries=1)
def get_processor(w_model, c_type, p_voice):
    return AudioProcessor(whisper_model=w_model, compute_type=c_type, piper_voice=p_voice)

processor = get_processor(whisper_model, compute_type, piper_voice)

for k, v in [("text", ""), ("audio", None), ("last_audio_hash", None), ("is_processing", False), ("voice_stats", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

audio_data = st.audio_input("Say something — tap to stop")

if audio_data and not st.session_state.is_processing:
    audio_bytes_val = audio_data.getvalue()
    current_hash = hashlib.sha256(audio_bytes_val).hexdigest()
    if current_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = current_hash
        st.session_state.is_processing = True
        st.rerun()

if st.session_state.is_processing and audio_data:
    with st.status("Running pipeline...", expanded=True) as status:
        try:
            audio_bytes_val = audio_data.getvalue()

            raw_text = processor.transcribe(audio_bytes_val)

            if not raw_text:
                status.update(label="No speech", state="complete", expanded=False)
            else:
                st.session_state.voice_stats = processor.analyze_voice_style(audio_bytes_val)
                st.session_state.text = raw_text
                st.session_state.audio = processor.synthesize(raw_text)
                status.update(label="Pipeline complete", state="complete", expanded=False)

        except Exception as e:
            st.error(f"Error: {e}")
            status.update(label="Error", state="error")
        finally:
            st.session_state.is_processing = False
            st.rerun()

if st.session_state.voice_stats:
    vs = st.session_state.voice_stats
    st.info(f"Pitch Std: {vs['pitch_std']} | Vol: {vs['volume']} | Arousal: {vs['arousal']} | Style: {vs['mood']}")
if st.session_state.audio:
    st.divider()
    st.text_area("Response:", st.session_state.text, height=120)
    st.audio(st.session_state.audio, format="audio/wav", autoplay=True)