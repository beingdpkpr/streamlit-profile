import streamlit as st
from os import path, getcwd


st.set_page_config(layout="wide", initial_sidebar_state="auto")
# Page Setup
home = st.Page(
    title="About Me",
    icon="🏠",
    page="views/home.py",
    default=True,
)

education = st.Page(
    title="Educations",
    icon="🎓",
    page="views/education.py",
)

work = st.Page(
    title="Work Experience",
    icon="💼",
    page="views/work.py",
)

skills = st.Page(
    title="Skills",
    icon="🛠️",
    page="views/skills.py",
)
certificates = st.Page(
    title="Certificates",
    icon="📜",
    page="views/certificates.py",
)

chatbot = st.Page(
    title="Chatbot",
    icon="💬",
    page="views/chatbot.py",
)

# qpa = st.Page(
#     title="Query Performance Analyzer",
#     icon="📊",
#     page="views/qpa.py",
# )

hierarchy_detector = st.Page(
    title="Hierarchy Detector",
    icon="📊",
    page="views/hierarchy-detector.py",
)

youtube_downloader = st.Page(
    title="Youtube Downloader",
    icon="📜",
    page="views/youtube-downloader.py",
)


# Navigation Setup
# pg = st.navigation(pages=[home, education, work, skills, chatbot])

# Navigation Configuration
pg = st.navigation(
    {
        "Info": [home, education, work, skills, certificates],
        # "Projects": [chatbot],
        "Projects": [hierarchy_detector, chatbot, youtube_downloader],
    },
)

# print(getcwd())
# print(path.isfile(path.join(getcwd(), "assets", "img2.jpg")))
logo_path = path.join("src", "assets", "img2.jpg")
st.logo(logo_path)
st.sidebar.text("Created by Deepak Prasad")

# Run Navigation
pg.run()
