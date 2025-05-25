import streamlit as st
import google.generativeai as genai
import os

st.title("💬 Chatbot")
# Configure API
api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
if not api_key:
    st.error("❌ Gemini API key not found in environment.")
    st.stop()

genai.configure(api_key=api_key)

# Load the model (no need to specify API version)
model = genai.GenerativeModel()

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        st.markdown(msg.parts[0].text)

if prompt := st.chat_input("Say something..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat.send_message(prompt)
    response = st.session_state.chat.last
    st.chat_message("assistant").markdown(response.text)
