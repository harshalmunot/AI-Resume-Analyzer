# ATS scoring engine
# score is 0-100 across 4 components:
#   - keyword coverage (50 pts)
#   - section completeness (20 pts)
#   - formatting (15 pts)
#   - semantic similarity (15 pts)

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.nlp_extractor import KeywordExtractor

# common resume sections and their regex patterns
# didn't want to hardcode exact names since resumes vary a lot
SECTION_PATTERNS = {
    "contact": r"(email|@|phone|linkedin|github)",
    "summary": r"(summary|objective|profile)",
    "skills": r"(skills|technologies|tech stack)",
    "experience": r"(experience|work history|employment)",
    "education": r"(education|university|college|degree|b\.tech|bachelor|master)",
    "projects": r"(projects|portfolio)",
}


class ATSScorer:
    """Calculates ATS compatibility score"""

    # weights for each component (should sum to 100)
    WEIGHTS = {
        "keyword_coverage": 50,
        "section_completeness": 20,
        "formatting": 15,
        "semantic_similarity": 15,
    }

    def score(self, resume_text, jd_text, resume_kw, jd_kw):
        # compute each component
        breakdown = {
            "keyword_coverage": self._keyword_score(resume_kw, jd_kw),
            "section_completeness": self._section_score(resume_text),
            "formatting": self._formatting_score(resume_text),
            "semantic_similarity": self._semantic_score(resume_text, jd_text),
        }

        total = sum(breakdown.values())

        # find matched/missing keywords for the report
        matched, missing = KeywordExtractor.overlap(resume_kw, jd_kw)

        # detect weak sections
        weak = self._find_weak_sections(resume_text)

        return {
            "ats_score": round(total),
            "breakdown": breakdown,
            "matched_keywords": matched[:25],   # cap at 25 to keep UI clean
            "missing_keywords": missing[:25],
            "weak_sections": weak,
        }

    def _keyword_score(self, resume_kw, jd_kw):
        """how many JD keywords are in the resume"""
        if not jd_kw:
            return self.WEIGHTS["keyword_coverage"]

        matched, _ = KeywordExtractor.overlap(resume_kw, jd_kw)
        ratio = len(matched) / max(1, len(set(jd_kw)))
        return round(ratio * self.WEIGHTS["keyword_coverage"])

    def _section_score(self, text):
        """how many standard sections the resume has"""
        text_lower = text.lower()
        present = 0
        for pattern in SECTION_PATTERNS.values():
            if re.search(pattern, text_lower):
                present += 1

        return round((present / len(SECTION_PATTERNS)) * self.WEIGHTS["section_completeness"])

    def _formatting_score(self, text):
        """basic formatting checks: length, bullets, contact info"""
        score = 0.0

        # length check - 300-1200 words is ideal for a resume
        word_count = len(text.split())
        if 300 <= word_count <= 1200:
            score += 0.5
        elif (200 <= word_count < 300) or (1200 < word_count <= 1500):
            score += 0.3

        # count lines that start with a bullet character
        lines = text.splitlines()
        bullet_count = 0
        for line in lines:
            stripped = line.strip()
            if re.match(r"^[\-\u2022\*]", stripped):
                bullet_count += 1

        if bullet_count >= 8:
            score += 0.25
        elif bullet_count >= 4:
            score += 0.15

        # contact info check - looking for email and phone patterns
        has_email = re.search(r"@\S+\.\S+", text)
        has_phone = re.search(r"\+?\d[\d\- ]{7,}\d", text)
        if has_email and has_phone:
            score += 0.25

        return round(score * self.WEIGHTS["formatting"])

    def _semantic_score(self, resume_text, jd_text):
        """cosine similarity between resume and JD"""
        if not resume_text.strip() or not jd_text.strip():
            return 0

        vec = TfidfVectorizer(ngram_range=(1, 2), max_features=500)
        try:
            matrix = vec.fit_transform([resume_text, jd_text])
            similarity = float(cosine_similarity(matrix[0], matrix[1])[0][0])
        except ValueError:
            similarity = 0.0

        return round(similarity * self.WEIGHTS["semantic_similarity"])

    def _find_weak_sections(self, text):
        """return list of section names that are missing"""
        text_lower = text.lower()
        weak = []
        for name, pattern in SECTION_PATTERNS.items():
            if not re.search(pattern, text_lower):
                weak.append(name.title())
        return weak
