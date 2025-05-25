import streamlit as st
from os import path
from variables import (
    name,
    title,
    profile_details,
    phone,
    email,
    linkedin,
    location,
    whatsapp,
    company,
)
from forms.contact import contact_form

left_column, right_column = st.columns([1, 3])


image_path = "assets/IMG.JPG"
resume_path = "assets/resume.pdf"


@st.dialog("Contact Me")
def show_contact_form():
    contact_form()


with left_column:
    if path.exists(image_path):
        st.image(image_path, width=230, use_container_width=True)

    else:
        st.error(f"Image not found at {image_path}. Please check the path.")

    st.markdown(
        f"""
        <h3><b>Details</b></h3>
        <p>
            📞 <i>{phone}</i>
            <br>
            🟢 <i>{whatsapp}</i>
            <br>
            ✉️ <i>{email}</i>
            <br>
            📍 {location}
            <br>
            🔗 <a href='{linkedin}'>Let's Connect on LinkedIn</a>
            <br>
        </p>
        """,
        unsafe_allow_html=True,
    )


with right_column:
    st.markdown(
        f"""
        <h1> {name} </h1>
        <h4> {title} </h4>
        <h5> {company} </h5>       
        <hr>
        <p> {profile_details} </p>
        <hr>
        """,
        unsafe_allow_html=True,
    )
    l_col, r_col = st.columns([1, 1])
    with l_col:
        if path.exists(resume_path):
            with open(resume_path, "rb") as f:
                st.download_button(
                    label="📄 Download Resume",
                    data=f,
                    file_name=resume_path,
                    mime="application/pdf",
                    help="Click to download my resume.",
                )
        else:
            st.error(f"Resume not found at {resume_path}. Please check the path.")
    with r_col:
        if st.button("✉️ Contact Me"):
            show_contact_form()
        # else:
        #     st.info("Click the button to contact me.")

st.markdown("<hr>", unsafe_allow_html=True)
