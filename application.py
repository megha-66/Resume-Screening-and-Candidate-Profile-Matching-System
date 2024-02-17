import streamlit as st
import pdfplumber
from Resume_scanner import compare
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def extract_pdf_data(file_path):
    data = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                data += text
    return data

# Function to send email
def send_email(email, subject, body):
    # Email configuration
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_username = "your_email@example.com"
    smtp_password = "your_password"

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = email
    msg['Subject'] = subject

    # Attach body to email
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, email, msg.as_string())


# Sidebar
flag = 'HuggingFace-BERT'
with st.sidebar:
    st.markdown('**Which embedding do you want to use**')
    options = st.selectbox('Which embedding do you want to use',
                           ['HuggingFace-BERT', 'Doc2Vec'],
                           label_visibility="collapsed")
    flag = options

# Main content
tab1, tab2, tab3 = st.tabs(["**Candidate Portal**", "**Results**", "**HR Portal**"])

# Tab Candidate Portal
with tab1:
    st.title("Applicant Tracking System")
    uploaded_files = st.file_uploader(
        '**Choose your resume.pdf file:** ', type="pdf", accept_multiple_files=True)
    JD = st.text_area("Enter the job description:")
    comp_pressed = st.button("Compare!")
    if comp_pressed and uploaded_files:
        # Streamlit file_uploader gives file-like objects, not paths
        uploaded_file_paths = [extract_pdf_data(
            file) for file in uploaded_files]
        score = compare(uploaded_file_paths, JD, flag)

# Tab Results
with tab2:
    st.header("Results")
    my_dict = {}
    if comp_pressed and uploaded_files:
        for i in range(len(score)):
            my_dict[uploaded_files[i].name] = score[i]
        sorted_dict = dict(sorted(my_dict.items()))
        for i in sorted_dict.items():
            with st.expander(str(i[0])):
                st.write("Score is: ", i[1])

# Tab HR Portal
with tab3:
    st.title("HR Portal")
    uploaded_hr_files = st.file_uploader(
        '**Upload resumes of candidates:** ', type="pdf", accept_multiple_files=True)
    JD_hr = st.text_area("Enter the job description: ")
    comp_pressed_hr = st.button("Compare Resumes!")
    if comp_pressed_hr and uploaded_hr_files:
        # Streamlit file_uploader gives file-like objects, not paths
        uploaded_hr_file_paths = [extract_pdf_data(
            file) for file in uploaded_hr_files]
        scores_hr = [compare([resume_data], JD_hr, flag) for resume_data in uploaded_hr_file_paths]

        # Rank resumes based on score
        ranked_resumes = sorted(zip(uploaded_hr_files, scores_hr), key=lambda x: x[1], reverse=True)
        for resume, score in ranked_resumes:
            st.write(f"The resume {resume.name} matches {score} of the job description.")

        # Email functionality
        send_email_option = st.checkbox("Send acceptance emails")
        reject_option = st.checkbox("Reject resumes")
        if send_email_option or reject_option:
            email_subject = st.text_input("Email Subject:")
            email_body = st.text_area("Email Body:")
            send_button = st.button("Send Emails")
            if send_button:
                for resume, score in ranked_resumes:
                    email = "candidate@example.com"  # Enter candidate's email here
                    threshold = 70
                    if send_email_option and score > threshold:  # Define threshold for acceptance
                        message = f"Congratulations! Your application has been accepted. {email_body}"
                        send_email(email, email_subject, message)
                    elif reject_option and score <= threshold:
                        message = f"We regret to inform you that your application was not successful. {email_body}"
                        send_email(email, email_subject, message)
                     
                     