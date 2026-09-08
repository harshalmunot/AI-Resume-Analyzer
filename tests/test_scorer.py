# tests for the ATS scoring engine
# run with: pytest tests/ -v

from app.services.scorer import ATSScorer


def test_keyword_coverage_full_overlap():
    # if all JD keywords are in resume, should get full points
    scorer = ATSScorer()
    result = scorer.score(
        resume_text="Python Flask REST API MySQL",
        jd_text="Looking for Python Flask MySQL developer",
        resume_keywords=["python", "flask", "rest api", "mysql"],
        jd_keywords=["python", "flask", "mysql"],
    )
    assert result["breakdown"]["keyword_coverage"] == 50


def test_weak_sections_detected():
    # skills-only resume should flag experience and education as weak
    scorer = ATSScorer()
    result = scorer.score(
        resume_text="Only skills: Java, Python",
        jd_text="Software engineer role",
        resume_keywords=["java", "python"],
        jd_keywords=["java"],
    )
    assert "Experience" in result["weak_sections"]
    assert "Education" in result["weak_sections"]


def test_score_in_range():
    # total score should always be between 0 and 100
    scorer = ATSScorer()
    resume = "email@x.com +919999999999\nSummary: SDE.\nSkills: Java\nExperience: Intern\nEducation: B.Tech\nProjects: X"
    result = scorer.score(resume, "Java role", ["java"], ["java"])
    assert 0 <= result["ats_score"] <= 100
