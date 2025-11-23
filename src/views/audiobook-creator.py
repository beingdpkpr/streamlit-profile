from gtts import gTTS
import streamlit as st
import tempfile

st.title("📘 Text To Audiobook Creator")


uploaded_file = st.file_uploader("Upload a TXT file", type="txt")
if uploaded_file:
    # Read the uploaded text file
    text = uploaded_file.read().decode("utf-8")

    st.subheader("Text Preview")
    st.write(text[:1000] + "..." if len(text) > 1000 else text)

    # Convert to speech button
    if st.button("Convert to Audio"):
        with st.spinner("Generating audio..."):
            # Create a temporary audio file
            tts = gTTS(text=text, lang="en")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)

        st.success("Audio Generated!")

        # Play audio in streamlit
        audio_file = open(temp_file.name, "rb").read()
        st.audio(audio_file, format="audio/mp3")

        # Download button
        st.download_button(
            label="Download MP3",
            data=audio_file,
            file_name="audiobook.mp3",
            mime="audio/mp3",
        )
