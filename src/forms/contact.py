import streamlit as st
from re import match
from yagmail import SMTP
from variables import email_contact, app_pass, email


def is_valid_email(_email):
    # Basic regex pattern for email validation
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return match(email_pattern, _email) is not None


def contact_form():
    with st.form("contact_form"):
        name = st.text_input("Name")
        user_email = st.text_input("Email")
        message = st.text_area("Message")
        submit_button = st.form_submit_button("Send Message")

    if submit_button:
        if not name:
            st.error("Please provide your name.", icon="🧑")
            st.stop()

        if not user_email:
            st.error("Please provide your email address.", icon="📨")
            st.stop()

        if not is_valid_email(user_email):
            st.error("Please provide a valid email address.", icon="📧")
            st.stop()

        if not message:
            st.error("Please provide a message.", icon="💬")
            st.stop()

        # Prepare the data payload and send it to the specified webhook URL
        data = f"""
            Name: {name}
            Email: {user_email} 
            Message: {message}
        """

        yag = SMTP(email_contact, app_pass)
        yag.send(email, f"{name} tried reaching you!", data)

        st.success(
            "Your message has been sent successfully! Thank you for reaching out.",
            icon="✅",
        )
