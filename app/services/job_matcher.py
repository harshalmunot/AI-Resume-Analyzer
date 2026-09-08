# job matcher
# takes the keywords extracted from the resume and finds the best-matching job roles
# scoring: required skills = 2x weight, preferred skills = 1x weight

import sys
import os

# add data folder to path so we can import job_roles
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "data"))
from job_roles import JOB_ROLES


class JobMatcher:
    """Recommends the top job roles based on resume skills"""

    # weights for scoring
    REQUIRED_WEIGHT = 2
    PREFERRED_WEIGHT = 1

    def match(self, resume_keywords, top_n=5):
        """
        find the top N matching job roles
        returns a list of role dicts sorted by match percentage
        """
        # normalize resume keywords to lowercase set for fast lookup
        resume_set = set(k.lower() for k in resume_keywords)

        results = []
        for role in JOB_ROLES:
            score_data = self._score_role(role, resume_set)
            results.append(score_data)

        # sort by percentage descending
        results.sort(key=lambda x: -x["match_percent"])

        return results[:top_n]

    def _score_role(self, role, resume_set):
        """calculate match score for a single role"""
        required = role["required"]
        preferred = role["preferred"]

        # count matched skills
        matched_required = [s for s in required if s in resume_set]
        matched_preferred = [s for s in preferred if s in resume_set]

        # missing skills (what user should learn)
        missing_required = [s for s in required if s not in resume_set]
        missing_preferred = [s for s in preferred if s not in resume_set]

        # calculate weighted score
        max_score = (len(required) * self.REQUIRED_WEIGHT) + (len(preferred) * self.PREFERRED_WEIGHT)
        actual_score = (
            len(matched_required) * self.REQUIRED_WEIGHT
            + len(matched_preferred) * self.PREFERRED_WEIGHT
        )

        if max_score == 0:
            percent = 0
        else:
            percent = round((actual_score / max_score) * 100)

        # boost slightly if all required skills are matched
        if len(matched_required) == len(required) and len(required) > 0:
            percent = min(100, percent + 5)   # small bonus for full required match

        return {
            "title": role["title"],
            "category": role["category"],
            "description": role["description"],
            "match_percent": percent,
            "matched_required": matched_required,
            "matched_preferred": matched_preferred,
            "missing_required": missing_required,
            "missing_preferred": missing_preferred[:5],   # limit for UI
            "total_matched": len(matched_required) + len(matched_preferred),
            "total_skills": len(required) + len(preferred),
        }
