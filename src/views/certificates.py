import streamlit as st

st.title("📜 Certificates")
st.markdown("---")

certificates = [
    {
        "title": "Python for Everybody (Specialization)",
        "issuer": "University of Michigan (Coursera)",
        "date": "May 1, 2017",
        "link": "https://www.coursera.org/account/accomplishments/specialization/certificate/UMHX9HMEFYZ6",
        "img": "assets/python_for_everybody_sp.jpg",
    },
    {
        "title": "Programming for Everybody (Getting Started with Python)",
        "issuer": "University of Michigan (Coursera)",
        "date": "May 1, 2017",
        "link": "https://www.coursera.org/account/accomplishments/certificate/F29FV3UC9NSU",
        "img": "assets/1_programming_for_everybody.jpg",
    },
    {
        "title": "Python Data Structures",
        "issuer": "University of Michigan (Coursera)",
        "date": "May 1, 2017",
        "link": "https://www.coursera.org/account/accomplishments/certificate/B9TUDRJRDRMM",
        "img": "assets/2_python_data_structure.jpg",
    },
    {
        "title": "Using Python to Access Web Data",
        "issuer": "University of Michigan (Coursera)",
        "date": "May 1, 2017",
        "link": "https://www.coursera.org/account/accomplishments/certificate/4BYNZT4XLYM6",
        "img": "assets/3_python_web_data.jpg",
    },
    {
        "title": "Using Databases with Python",
        "issuer": "University of Michigan (Coursera)",
        "date": "May 3, 2017",
        "link": "https://www.coursera.org/account/accomplishments/certificate/ELRKSWCFW6HG",
        "img": "assets/4_python_databases.jpg",
    },
    {
        "title": "Capstone: Retrieving, Processing, and Visualizing Data with Python",
        "issuer": "University of Michigan (Coursera)",
        "date": "May 4, 2017",
        "link": "https://www.coursera.org/account/accomplishments/certificate/QEXUR86WJK2A",
        "img": "assets/5_python_capstone.jpg",
    },
    {
        "title": "IBM Blockchain Foundation for Developers",
        "issuer": "IBM (Coursera)",
        "date": "December 7, 2017",
        "link": "https://www.coursera.org/account/accomplishments/certificate/CQRKEMJ5S7MR",
        "img": "assets/IBM_blockchain.jpg",
    },
    {
        "title": "Programming Foundations with JavaScript, HTML and CSS",
        "issuer": "Duke University (Coursera)",
        "date": "December 13, 2017",
        "link": "https://www.coursera.org/account/accomplishments/certificate/GFYAS78H7D7L",
        "img": "assets/web_foundation.jpg",
    },
    {
        "title": "Introduction to Data Science (Specialization)",
        "issuer": "IBM (Coursera)",
        "date": "January 1, 2021",
        "link": "https://www.coursera.org/account/accomplishments/specialization/certificate/RVJWUCUESX9A",
        "img": "assets/data_science_sp.jpg",
    },
    {
        "title": "What is Data Science?",
        "issuer": "IBM (Coursera)",
        "date": "January 2, 2021",
        "link": "https://www.coursera.org/account/accomplishments/certificate/GMA24YMD3N26",
        "img": "assets/1_what_is_ds.jpg",
    },
    {
        "title": "Tools for Data Science",
        "issuer": "IBM (Coursera)",
        "date": "January 1, 2021",
        "link": "https://www.coursera.org/account/accomplishments/certificate/PCEAYQV8Q2WL",
        "img": "assets/2_ds_tools.jpg",
    },
    {
        "title": "Data Science Methodology",
        "issuer": "IBM (Coursera)",
        "date": "January 2, 2021",
        "link": "https://www.coursera.org/account/accomplishments/certificate/HN5VWMX9L685",
        "img": "assets/3_ds_methodology.jpg",
    },
    {
        "title": "Databases and SQL for Data Science with Python",
        "issuer": "IBM (Coursera)",
        "date": "January 2, 2021",
        "link": "https://www.coursera.org/account/accomplishments/certificate/A5J445CLAHHC",
        "img": "assets/4_ds_databases_sql.jpg",
    },
]

# Custom CSS
st.markdown(
    """
    <style>
        .cert-card {
            background: linear-gradient(135deg, #f0f2f5, #ffffff);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .cert-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .cert-title {
            font-weight: 600;
            font-size: 17px;
            margin-bottom: 4px;
            color: #1f2937;
        }
        .cert-issuer {
            font-size: 14px;
            color: #4b5563;
        }
        .cert-date {
            font-size: 13px;
            color: #9ca3af;
            margin-bottom: 8px;
        }
        .cert-link a {
            font-size: 13px;
            color: #2563eb;
            text-decoration: none;
        }
        .cert-link a:hover {
            text-decoration: underline;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Display in two columns
col1, col2 = st.columns(2, gap="large")


for i, cert in enumerate(certificates):
    caption = f"📄 {cert['title']}"
    card_html = f"""
    <div class='cert-card'>
        <div class='cert-title'>{cert["title"]}</div>
        <div class='cert-issuer'>{cert["issuer"]}</div>
        <div class='cert-date'>{cert["date"]}</div>
        <div class='cert-link'><a href='{cert["link"]}' target='_blank'>🔗 {caption}</a></div>
    </div>
    """

    if i % 2 == 0:
        col1.image(cert["img"], use_container_width=True)
        col1.markdown(card_html, unsafe_allow_html=True)
        col1.markdown("---")
    else:
        col2.image(cert["img"], use_container_width=True)
        col2.markdown(card_html, unsafe_allow_html=True)
        col2.markdown("---")
