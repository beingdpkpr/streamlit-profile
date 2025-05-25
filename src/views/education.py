import streamlit as st

st.title("🎓 Education")
st.markdown("---")

education_data = [
    {
        "degree": "Bachelor of Engineering",
        "field": "Computer Science & Engineering",
        "university": "Sri Jayachamarajendra College of Engineering, Mysore (SJCE)",
        "percentage": "8.01",
        "year": "2016",
        "projects": [
            {
                "title": "Gender Recognition based on Palm-print",
                "subject": "Pattern Recognition",
                "description": (
                    "Captured palm-print images and classified gender based on biometric dimensions "
                    "such as palm width and finger length using image processing techniques."
                ),
                "technologies": "Matlab, Image Processing",
            },
            {
                "title": "Congestion Control",
                "subject": "Computer Networks",
                "description": (
                    "Implemented priority-based load shedding to manage congestion in high-traffic networks."
                ),
                "technologies": "C programming",
            },
            {
                "title": "Web Tutorial",
                "subject": "Web Technologies",
                "description": (
                    "Developed a tutorial website offering video and text-based content to assist student learning."
                ),
                "technologies": "HTML, CSS and JavaScript",
            },
        ],
        "achievement": [],
    },
    {
        "degree": "All India Senior Secondary Certificate Examination (AISSCE)",
        "field": "Class XII with Science (CBSE)",
        "university": "Jawahar Navodaya Vidyalaya, Bishnupur (JNV)",
        "percentage": "89.8",
        "year": "2011",
        "projects": [],
        "achievement": [
            "Secured high distinction in Mathematics.",
            "Represented school at the Regional Mathematics Exhibition.",
        ],
    },
    {
        "degree": "All India Secondary Certificate Examination (AISCE)",
        "field": "Class X (CBSE)",
        "university": "Jawahar Navodaya Vidyalaya, Bishnupur (JNV)",
        "percentage": "88.8",
        "year": "2009",
        "projects": [],
        "achievement": [
            "Represented school at the Regional Table Tennis tournament.",
            "Scored 99/100 in Mathematics.",
        ],
    },
]

for edu in education_data:
    with st.expander(f"{edu['degree']}", expanded=True):
        st.markdown(
            f"<h3 style='text-align: center'>{edu['degree']}</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h6 style='text-align: center'>{edu['field']}</h6><hr>",
            unsafe_allow_html=True,
        )
        l_column, r_column = st.columns([1, 3])
        with l_column:
            st.markdown(f"**Institute / University:**")
            st.markdown(f"---")
            st.markdown(f"**Grade / Percentage:**")
            st.markdown(f"---")
            st.markdown(f"**Year of Completion:**")
            st.markdown(f"---")
        with r_column:
            st.markdown(f"{edu['university']}")
            st.markdown(f"---")
            st.markdown(f"{edu['percentage']}")
            st.markdown(f"---")
            st.markdown(f"{edu['year']}")
            st.markdown(f"---")

        left_column, right_column = st.columns([1, 3])
        if len(edu["projects"]) > 0:
            with left_column:
                st.markdown(f"**Projects:**")
            for project in edu["projects"]:
                with right_column:
                    st.markdown(f"**{project['title']}**")
                    st.markdown(f"{project['description']}")
                    st.markdown(f"*Technologies Used:* {project['technologies']}")
                    st.markdown("---")
        if len(edu["achievement"]) > 0:
            with left_column:
                st.markdown(f"**Achievements:**")
            for achievement in edu["achievement"]:
                with right_column:
                    st.markdown(f"- {achievement}")
