# tests for keyword extraction

from app.services.nlp_extractor import KeywordExtractor


def test_taxonomy_hits():
    # should find skills from the taxonomy file
    ex = KeywordExtractor()
    kws = ex.extract("I built a Flask + Python REST API with MySQL and JWT auth.")
    assert "flask" in kws
    assert "python" in kws
    assert "mysql" in kws


def test_overlap():
    # basic overlap check
    matched, missing = KeywordExtractor.overlap(
        ["Python", "Flask"],
        ["python", "docker"]
    )
    assert matched == ["python"]
    assert missing == ["docker"]
