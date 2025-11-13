from datetime import datetime

name = "Deepak Prasad"

title = "Senior Application Architect"
company = "o9 Solutions Inc."
work_start_date = "2016-06-01"
gap_months = 5  # 6 months gap in experience

start = datetime.strptime(work_start_date, "%Y-%m-%d")
now = datetime.now()
total_months = (now.year - start.year) * 12 + (now.month - start.month) - gap_months

total_experience_years = total_months // 12
total_months = total_months % 12

profile_details = f"""
    Dynamic Software Engineer with around {total_experience_years} years, {total_months} months of experience in software development and architecture.
    Proficient in leading projects to enhance performance and optimize functionalities across multiple platforms.
    Successfully mentored teams to achieve project milestones, while optimizing supply planning plugins and
    developing innovative applications in Python and Angular. Proven ability to drive significant improvements in
    operational efficiency, positioning to deliver exceptional value in software architecture roles.
    Passionate about creating and innovating, driven to make a difference and leave the world a better place.
"""
phone = "+91 8861 327919"
whatsapp = "+1 (707) 733 3727"
linkedin = "https://www.linkedin.com/in/dpkpr1/"
location = "Bangalore, India"
email_contact = "deepak.prasad.ai+website@gmail.com"
