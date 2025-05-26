import streamlit as st

# Inject Custom CSS for modern UI
st.markdown(
    """
    <style>
        /* General styles */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .skill-container {
            margin-bottom: 16px;
        }

        .skill-name {
            font-weight: 600;
            font-size: 16px;
            # margin-bottom: 4px;
        }

        /* Badge style for development environment */
        .env-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 12px;
            margin: 6px 8px 6px 0;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            transition: transform 0.2s ease-in-out;
        }

        .env-badge:hover {
            transform: scale(1.15);
        }

        /* Progress bar style override */
        .stProgress > div > div {
            background-image: linear-gradient(to right, #00c6ff, #0072ff);
        }

    </style>
""",
    unsafe_allow_html=True,
)

# Title
st.title("🛠️ Skills Overview")
st.markdown("---")

# Define skills
professional_skills = {
    "Python": 5,
    "Data Analysis": 5,
    "SQL": 4,
    "HTML, CSS & JavaScript/TypeScript": 4,
    "Angular & Bootstrap": 4,
    "SVN, GIT": 4,
    "Architecture & Design": 4,
    "o9 Platform & Solver": 4,
    "Streamlit": 3,
    "Supply Chain Management": 3,
    "Docker": 3,
    "Java": 3,
    "Data Science": 3,
    "C/C++": 2,
    "Android": 2,
    "Elasticsearch & Redis": 2,
}

personal_skills = {
    "Problem Solving": 5,
    "Team Work": 5,
    "Troubleshoot & Debugging": 5,
    "Dedication": 5,
    "Communication": 4,
    "Adaptability": 4,
    "Time Management": 4,
    "Leadership": 4,
}

development_environment = [
    "Windows",
    "Linux",
    "Visual Studio Code",
    "PyCharm",
    "Eclipse",
    "IntelliJ IDEA",
    "Android Studio",
]

# Two-column layout
col1, col2 = st.columns(2)

# --- Professional Skills ---
with col1:
    st.subheader("👨‍💻 Professional Skills")
    for skill, level in professional_skills.items():
        with st.container():
            st.markdown(
                f"<div class='skill-name'>{skill}</div>", unsafe_allow_html=True
            )
            st.progress(level / 5)

# --- Personal Skills ---
with col2:
    st.subheader("🧠 Personal Skills")
    for skill, level in personal_skills.items():
        with st.container():
            st.markdown(
                f"<div class='skill-name'>{skill}</div>", unsafe_allow_html=True
            )
            st.progress(level / 5)

# --- Development Environment ---
st.subheader("💻 Development Environments")
badge_html = "".join(
    [f"<span class='env-badge'>{env}</span>" for env in development_environment]
)
st.markdown(
    f"<div style='margin-top: 10px;'>{badge_html}</div>", unsafe_allow_html=True
)
