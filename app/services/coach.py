# AI career coach (chat)
# answers questions about the resume analysis.
# two modes:
#   1. rule-based (default) - uses the analysis report the frontend sends
#   2. if OPENAI_API_KEY is set, delegates to gpt-3.5/4 for free-form answers

import os
import re


class CareerCoach:
    """simple chatbot that knows about the last analysis"""

    def __init__(self):
        self.openai_available = False
        try:
            # optional - only if user has a key
            from openai import OpenAI  # noqa
            if os.environ.get("OPENAI_API_KEY"):
                self.openai_available = True
        except ImportError:
            self.openai_available = False

    def answer(self, message, context=None):
        """returns a reply string + optional follow-up suggestions"""
        context = context or {}
        message = message.strip().lower()

        # greetings
        if re.search(r"\b(hi|hello|hey|namaste)\b", message):
            return ("Hello! I'm here to help you land interviews. "
                    "Ask me about improving your ATS score, missing keywords, "
                    "or which jobs fit your skills."), []

        # score questions
        if re.search(r"(score|how did i do|percentage)", message) and context.get("ats_score") is not None:
            score = context["ats_score"]
            if score >= 85:
                tip = "You're in strong shape! Focus on tailoring the summary per JD."
            elif score >= 70:
                tip = "Good base. Add missing keywords and quantify more bullets."
            else:
                tip = "Needs work. Mirror the JD's vocabulary in your skills section."
            return (f"Your ATS score for the last JD was {score}/100. {tip}"), []

        # improvement questions
        if re.search(r"(improve|better|optimize|fix|enhance)", message):
            missing = context.get("missing_keywords") or []
            tips = context.get("suggestions") or []
            reply = []
            if missing:
                reply.append("Biggest win: add missing JD keywords like "
                             + ", ".join(missing[:5]) + " to your Skills/Experience.")
            if tips:
                reply.append("Short from your report: " + tips[0])
            if not reply:
                reply.append("Upload a resume + JD first, then ask me again.")
            return (" ".join(reply)), ["Add metrics to project bullets",
                                       "Rewrite summary to target the role",
                                       "Mirror JD keywords exactly"]

        # job match questions
        if re.search(r"(which job|what job|suit|best role|job match)", message):
            matches = context.get("job_matches") or []
            if matches:
                top = matches[0]
                return (f"Right now your best fit is '{top['title']}' at {top['match_percent']}% match. "
                        "Next in line: " + ", ".join(m["title"] for m in matches[1:3]) +
                        ". Focus on missing required skills to raise these."), []
            return ("Run a job match first (switch to Job Match Only mode), then ask me."), []

        # skill questions
        if re.search(r"(skill|which tech|what to learn)", message):
            matches = context.get("job_matches") or []
            missing = []
            for m in matches[:3]:
                missing.extend(m.get("missing_required") or [])
            missing = list(dict.fromkeys(missing))[:6]
            if missing:
                return ("Skills worth learning for your top roles: " + ", ".join(missing) +
                        ". Start with the one that appears in the most roles."), []
            return ("Based on what I see, keep deepening your strongest stack. "
                    "Add a cloud skill like AWS or Docker for a big boost."), []

        # cover letter / templates features
        if re.search(r"(cover letter|template)", message):
            return ("Check the Cover Letter and Templates tabs above - "
                    "I can generate a tailored cover letter from your resume + JD, "
                    "and export your resume in 3 different styles."), []

        # thanks
        if re.search(r"(thank|thanks)", message):
            return "You're welcome! Go get that offer. 🚀", []

        # fallback
        return ("I can help with questions like:\n"
                "- 'how do I improve?' (based on your last analysis)\n"
                "- 'which jobs suit me?'\n"
                "- 'what skills should I learn?'"), [
            "How do I improve?",
            "Which jobs suit me?",
            "What skills should I learn?",
        ]

    def ask_llm(self, message, context):
        """optional: delegate to OpenAI if configured"""
        if not self.openai_available:
            return None
        from openai import OpenAI
        client = OpenAI()
        prompt = f"""You are a career coach for a CS student.
            Context from their resume analysis: {context}
            Answer briefly and practically."""
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message},
                ],
                max_tokens=200,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return None
