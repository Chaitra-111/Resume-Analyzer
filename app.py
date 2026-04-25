from flask import Flask, render_template, request
import os
import re
from PyPDF2 import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = "resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Predefined Job Roles
job_roles = {
    "Python Developer": "Looking for a Python developer with strong skills in Python, SQL, data analysis, and machine learning. Good communication skills and Excel knowledge required.",
    
    "Data Analyst": "Seeking a Data Analyst with skills in Python, SQL, data analysis, and Excel. Candidate should have good communication skills and reporting abilities.",
    
    "Software Developer": "Looking for a Software Developer with knowledge of Python, Java, SQL, and problem-solving skills. Good communication is required.",
    
    "ML Intern": "Hiring a Machine Learning Intern with knowledge of Python, machine learning, data analysis, and SQL. Communication skills are important."
}

skills_list = [
    "python", "java", "sql", "machine learning",
    "data analysis", "communication", "excel"
]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    return text

def extract_skills(text):
    return [skill for skill in skills_list if skill in text]

def extract_text_from_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

def calculate_score(resume, job_desc):
    return sum(1 for skill in skills_list if skill in resume and skill in job_desc)

@app.route("/")
def index():
    return render_template("index.html", roles=job_roles)

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]
    selected_role = request.form["role"]

    # Get JD from selected role
    job_desc = job_roles.get(selected_role, "")

    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        return "❌ Only TXT and PDF allowed"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    if file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(filepath)
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            resume_text = f.read()

    resume_text = clean_text(resume_text)
    job_desc = clean_text(job_desc)

    skills = extract_skills(resume_text)
    score = calculate_score(resume_text, job_desc)

    missing = [s for s in skills_list if s not in resume_text]

    job_skills = [s for s in skills_list if s in job_desc]
    percentage = (score / len(job_skills)) * 100 if job_skills else 0

    return render_template("result.html",
                           skills=skills,
                           score=score,
                           missing=missing,
                           percentage=round(percentage, 2),
                           role=selected_role)

if __name__ == "__main__":
    app.run(debug=True)