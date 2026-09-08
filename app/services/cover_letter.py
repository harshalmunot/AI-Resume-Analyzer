# cover letter generator
# builds a tailoring cover letter from resume text + job description
# picks the best matching skills + top projects and weaves them into a template
# keeps it simple: 4 paragraphs structure

import re
import datetime


def generate_cover_letter(resume_text, jd_text, user_name=None, job_title=None):
    """
    returns a dict with the cover letter (plain text) and some meta info
    """
    # extract some info to customize the letter
    skills = extract_skills(resume_text, limit=6)
    jd_skills = extract_skills(jd_text, limit=4)
    projects = extract_projects(resume_text, limit=2)
    education = extract_education(resume_text)
    name = (user_name or "YOUR NAME")
    today = datetime.date.today().strftime("%B %d, %Y")

    # derive a job title if not given
    if not job_title:
        job_title = "Software Engineering Intern"

    # build the paragraphs
    intro = (
        f"Dear Hiring Manager,\n\n"
        f"I am writing to apply for the {job_title} position. As a "
        f"{education} with hands-on experience in {skills_text(skills)}, "
        f"I am excited about the opportunity to contribute to your team."
    )

    body1 = ""
    if jd_skills:
        body1 = (
            f"\n\nYour posting emphasizes {skills_text(jd_skills)}, which are exactly the "
            f"areas I have been building my skills in. I have applied these in real projects "
            f"and I am confident I can add value from day one."
        )

    body2 = ""
    if projects:
        body2 = (
            f"\n\nHighlighting one of my key projects: {projects[0]}. Working on this "
            f"taught me how to take an idea from architecture to a working, tested "
            f"implementation - exactly the kind of ownership I would bring to this role."
        )

    close = (
        f"\n\nI would welcome the chance to discuss how my background fits your needs. "
        f"Thank you for your time and consideration.\n\n"
        f"Sincerely,\n{name}\n"
        f"{today}"
    )

    full_text = intro + body1 + body2 + close

    return {
        "cover_letter": full_text,
        "meta": {
            "name": name,
            "skills_used": skills,
            "jd_skills_used": jd_skills,
            "project_used": projects[0] if projects else None,
            "education": education,
        },
    }


# --- small helpers --------------------------------------------------------

def extract_skills(text, limit=6):
    # very light keyword list (reuses the concept from the scorer)
    common = [
        "python", "java", "c++", "javascript", "flask", "spring boot", "rest api",
        "mysql", "mongodb", "docker", "kubernetes", "aws", "git", "nlp", "pandas",
        "numpy", "scikit-learn", "react", "sql", "html", "css", "oop", "agile",
    ]
    found = []
    lower = text.lower()
    for skill in common:
        if re.search(r"\b" + re.escape(skill) + r"\b", lower):
            found.append(skill)
            if len(found) >= limit:
                break
    return found


def extract_projects(text, limit=2):
    # naive: look for lines under a projects heading that look like titles
    lines = text.splitlines()
    projects = []
    capture = False
    for line in lines:
        low = line.lower()
        if re.search(r"(projects|portfolio)", low):
            capture = True
            continue
        if capture:
            if re.search(r"(education|experience|skills|certifications|summary)", low):
                break
            # skip bullets and tech lines, keep title-ish lines
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith(("-", "*", "•", "Technolog", "Built", "Developed", "Designed"))
                and len(stripped) > 8
                and not re.match(r"^[A-Za-z0-9, ]{1,15}:", stripped)
            ):
                projects.append(stripped)
            if len(projects) >= limit:
                break
    return projects


def extract_education(text):
    m = re.search(r"(B\.?Tech|Bachelor|Master|M\.?Tech|MBA)[^(\n]{0,80}", text, re.IGNORECASE)
    if m:
        return m.group(0).strip()
    return "Computer Science student"


def skills_text(skills):
    """ 'Python, Flask, and MySQL' style join """
    if not skills:
        return "programming fundamentals"
    if len(skills) == 1:
        return skills[0]
    return ", ".join(skills[:-1]) + ", and " + skills[-1]
