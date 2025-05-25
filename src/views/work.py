import streamlit as st
from datetime import datetime

st.title("💼 Work Experience")
st.markdown("---")

work_experience_data = [
    {
        "job_title": "Senior Application Architect",
        "company": "o9 Solutions Inc.",
        "start_date": "2019-08-01",
        "end_date": "",
        "location": "Bengaluru, India",
        "domain": [
            "Application development",
            "Supply Chain Management",
            "o9 Platform",
            "Performance Tuning",
        ],
        "projects": [
            {
                "title": "Tenant Builder",
                "description": "Automated tenant creation by consuming data from the Tenant Extractor app.",
                "technologies": "Python, SQLite, ANTLR, Web APIs",
                "role": "Design & Development",
                "responsibilities": (
                    "Led end-to-end development. Generated DDL queries from extracted data and triggered them "
                    "via API calls for tenant configuration."
                ),
            },
            {
                "title": "Rule Creator",
                "description": "Bulk rule creation utility for the o9 Platform.",
                "technologies": "Python, ANTLR, Web APIs",
                "role": "Design & Development",
                "responsibilities": (
                    "Built functionality to add multiple rules in batch using API calls, enhancing platform "
                    "productivity."
                ),
            },
            {
                "title": "Query Performance Analyzer (QPA)",
                "description": "Tool for analyzing and improving query performance in o9 Platform.",
                "technologies": "Python, Angular, Web APIs",
                "role": "Design & Development",
                "responsibilities": "Built and maintained a tool to track and optimize query performance metrics.",
            },
            {
                "title": "Demand Netting Plugin",
                "description": "Calculated net demand from orders, forecast, and RTF data.",
                "technologies": "Python, Pandas, SQLite",
                "role": "Design & Development",
                "responsibilities": (
                    "Developed logic to consume forecast and RTF to assign correct order types based on netting rules."
                    " Improved performance by 80% by optimizing data processing and storage."
                ),
            },
            {
                "title": "Custom Plugins for Supply Planning",
                "description": "Developed multiple custom plugins for client-specific needs.",
                "technologies": "Python, Pandas, PySpark, Delta Lake",
                "role": "Architect & Developer",
                "responsibilities": (
                    "Understood business needs and implemented plugins to enhance supply planning workflows."
                ),
            },
            {
                "title": "Where Used Plugin",
                "description": "Network traversal tool for dependency analysis in BOM.",
                "technologies": "NetworkX, Pandas",
                "role": "Architect & Developer",
                "responsibilities": (
                    "Designed plugin to identify all usages of a node/component in the supply network."
                ),
            },
            {
                "title": "Order Promising Plugin",
                "description": "Calculated feasible delivery dates for orders.",
                "technologies": "Pandas",
                "role": "Architect & Developer",
                "responsibilities": "Developed algorithm to commit orders based on supply visibility.",
            },
            {
                "title": "SP Product Re-architecture",
                "description": "Improved performance and memory efficiency of Supply Planning (SP) products.",
                "technologies": "Wireframes, REST APIs, Python",
                "role": "Architect",
                "responsibilities": "Redesigned architecture to reduce memory footprint and improve execution time.",
            },
        ],
    },
    {
        "job_title": "Software Engineer - Python",
        "company": "o9 Solutions Inc. (Contracted by MIPL)",
        "start_date": "2019-02-18",
        "end_date": "2019-07-31",
        "location": "Bengaluru, India",
        "domain": [
            "Application development",
            "o9 Platform",
        ],
        "projects": [
            {
                "title": "Tenant Extractor",
                "description": "Extracted and structured data from o9 tenant config files.",
                "technologies": "Python, Data Mining, SQLite, Pandas",
                "role": "Developer",
                "responsibilities": (
                    "Designed and developed an app to mine critical information from tenant JSON and export to "
                    "SQLite, CSV, and Excel."
                ),
            },
        ],
    },
    {
        "job_title": "Associate Software Engineer",
        "company": "PrimeSoft Solutions, Inc.",
        "start_date": "2016-06-01",
        "end_date": "2018-07-31",
        "location": "Bengaluru, India",
        "domain": [
            "Networking",
            "Network Security",
            "DevOps",
            "Application development",
            "Web development",
        ],
        "projects": [
            {
                "title": "Google API Integration",
                "description": "Researched and integrated Google services with internal applications.",
                "technologies": "REST APIs, OAuth 2.0, Python",
                "role": "Developer",
                "responsibilities": (
                    "Integrated APIs for YouTube, Google Calendar, Picasa, and Tasks with secure auth flows."
                ),
            },
            {
                "title": "Enterprise Security Project",
                "description": (
                    "Developed modules for securing critical enterprise assets using asset gateways and authentication controllers."
                ),
                "technologies": "Java, Docker, Tomcat",
                "role": "Developer",
                "responsibilities": (
                    "Stabilized legacy components and built new features to improve system robustness."
                ),
            },
            {
                "title": "Monitoring & Patching",
                "description": (
                    "Built tools for monitoring on-prem/cloud infrastructure and automated patching."
                ),
                "technologies": "Splunk, Microsoft Azure, Shavlik, Python",
                "role": "DevOps Engineer",
                "responsibilities": (
                    "Developed scripts and tools for system health monitoring and patch lifecycle management."
                ),
            },
            {
                "title": "Attendance Management System",
                "description": (
                    "Automated enterprise attendance and visitor management through an Android app."
                ),
                "technologies": "Android Studio, Java",
                "role": "Mobile Developer",
                "responsibilities": "End-to-end development of the Android app.",
            },
        ],
    },
]

for work in work_experience_data:
    with st.expander(f"{work['job_title']}", expanded=True):
        st.markdown(
            f"<h3 style='text-align: center'>{work['job_title']}</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h6 style='text-align: center'>{work['company']}</h6><hr>",
            unsafe_allow_html=True,
        )
        l_column, r_column = st.columns([1, 3])
        with l_column:
            st.markdown(f"**Total Experience:**")
            st.markdown(f"---")
            st.markdown(f"**Domain Experience:**")
            st.markdown(f"---")
        with r_column:
            start_date = datetime.strptime(work["start_date"], "%Y-%m-%d")
            if work["end_date"]:
                end_date = datetime.strptime(work["end_date"], "%Y-%m-%d")
            else:
                end_date = datetime.now()
            total_months = (end_date.year - start_date.year) * 12 + (
                end_date.month - start_date.month
            )
            years = total_months // 12
            months = total_months % 12 + 1

            st.markdown(f"{years} years, {months} months")
            st.markdown(f"---")
            st.markdown(f"{', '.join(work['domain'])}")
            st.markdown(f"---")

        left_column, right_column = st.columns([1, 3])

        if len(work["projects"]) > 0:
            with left_column:
                st.markdown(f"**Projects:**")
            count = 1
            for project in work["projects"]:
                with right_column:
                    st.markdown(f"**{count}. {project['title']}**")
                    st.markdown(f"{project['description']}")
                    st.markdown(f"*Responsibilities:* {project['responsibilities']}")
                    st.markdown(f"*Roles:* {project['role']}")
                    st.markdown(f"*Technologies Used:* {project['technologies']}")
                    st.markdown("---")
                count += 1
