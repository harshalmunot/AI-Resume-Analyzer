# builds personalized suggestions based on the score report
# tries to give actionable advice, not generic tips

class SuggestionEngine:

    def build(self, report, resume_text):
        tips = []

        # tip 1: missing keywords
        missing = report.get("missing_keywords") or []
        if missing:
            top5 = ", ".join(f"'{k}'" for k in missing[:5])
            tips.append(
                f"Add these high-priority keywords from the JD to your Skills or Experience: {top5}."
            )

        # tip 2: weak sections
        weak = report.get("weak_sections") or []
        if weak:
            tips.append(
                f"Your resume is missing/weak in these sections: {', '.join(weak)}. "
                "Add a dedicated section for each."
            )

        # tip 3: length check
        word_count = len(resume_text.split())
        if word_count < 300:
            tips.append(
                f"Your resume is only ~{word_count} words - flesh out project bullets with metrics and impact."
            )
        elif word_count > 1200:
            tips.append(
                f"Your resume is ~{word_count} words - trim to 1 page (~600-900 words) for internship roles."
            )

        # tip 4: low keyword coverage
        breakdown = report.get("breakdown", {})
        if breakdown.get("keyword_coverage", 0) < 25:
            tips.append(
                "Keyword coverage is low - mirror 3-5 exact phrases from the JD in your Skills section."
            )

        # tip 5: low semantic similarity
        if breakdown.get("semantic_similarity", 0) < 8:
            tips.append(
                "Your resume's overall vocabulary differs from the JD - tune the Summary to the target role."
            )

        # tip 6: not enough metrics/numbers
        if count_digits_ratio(resume_text) < 0.02:
            tips.append(
                "Very few numbers in your bullets - quantify at least 3 project outcomes "
                "(users, requests, latency, %)."
            )

        # fallback if everything is fine
        if not tips:
            tips.append("Great job - resume looks well aligned with the JD.")

        return tips


def count_digits_ratio(text):
    """what fraction of characters are digits"""
    if not text:
        return 0.0

    digit_count = 0
    for ch in text:
        if ch.isdigit():
            digit_count += 1

    return digit_count / max(1, len(text))
