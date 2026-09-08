# keyword extractor
# uses two approaches together:
#   1. match against a skills taxonomy file (high precision)
#   2. TF-IDF top terms (catches stuff not in the taxonomy)

import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# basic stopwords - didn't want to import nltk stopwords everywhere
STOPWORDS = {
    "the", "and", "or", "of", "to", "a", "an", "in", "on", "for", "with",
    "at", "by", "from", "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "as", "that", "this",
    "these", "those", "it", "its", "i", "you", "he", "she", "we", "they",
    "our", "your", "their",
}

# regex for tokenizing - allows things like c++, node.js, .net
TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9\+\#\.\-]*")


def load_skills():
    """load the curated skills list from the data folder"""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "skills_taxonomy.txt")
    if not os.path.exists(path):
        return set()

    skills = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                skills.add(line.lower())
    return skills


class KeywordExtractor:
    """Extracts skills and keywords from resume/JD text"""

    def __init__(self, top_n=40):
        self.top_n = top_n
        self.skills = load_skills()

    def extract(self, text):
        """returns a sorted list of keywords found in text"""
        text_lower = text.lower()
        found = set()

        # step 1: check taxonomy matches
        # using word boundaries so 'java' doesn't match 'javascript'
        for skill in self.skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found.add(skill)

        # step 2: TF-IDF for extra keywords not in taxonomy
        tokens = self._tokenize(text_lower)
        if tokens:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=200,
                stop_words=list(STOPWORDS),
            )
            try:
                matrix = vectorizer.fit_transform([" ".join(tokens)])
                terms = vectorizer.get_feature_names_out()
                scores = matrix.toarray()[0]

                # sort by score, take top N
                pairs = sorted(zip(terms, scores), key=lambda x: -x[1])
                for term, score in pairs[:self.top_n]:
                    if score > 0 and len(term) > 1:
                        found.add(term)
            except ValueError:
                # empty vocabulary - skip
                pass

        return sorted(found)

    def _tokenize(self, text):
        tokens = TOKEN_PATTERN.findall(text)
        # remove stopwords and short tokens
        return [t for t in tokens if t.lower() not in STOPWORDS and len(t) > 1]

    @staticmethod
    def overlap(resume_kw, jd_kw):
        """find matched and missing keywords between resume and JD"""
        resume_set = {k.lower() for k in resume_kw}
        jd_list = [k.lower() for k in jd_kw]

        matched = [k for k in jd_list if k in resume_set]
        missing = [k for k in jd_list if k not in resume_set]

        # dedupe
        return sorted(set(matched)), sorted(set(missing))
