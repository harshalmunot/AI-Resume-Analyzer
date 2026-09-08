import io
import time
from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename

from app.services.parser import extract_text
from app.services.nlp_extractor import KeywordExtractor
from app.services.scorer import ATSScorer
from app.services.suggester import SuggestionEngine
from app.services.job_matcher import JobMatcher
from app.services.translations import get_translations, LANG_NAMES
from app.services.cover_letter import generate_cover_letter
from app.services.linkedin_import import fetch_profile, build_resume_text_from_profile
from app.services import resume_templates
from app.services.coach import CareerCoach

bp = Blueprint("main", __name__)


def is_allowed_file(filename):
    # check if file extension is pdf or docx
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def extract_resume_or_400():
    """parse the uploaded resume, return (text, error_response)"""
    if "resume" not in request.files:
        return None, (jsonify({"error": "resume file is required"}), 400)

    file = request.files["resume"]
    if not file or file.filename == "":
        return None, (jsonify({"error": "empty file"}), 400)

    if not is_allowed_file(file.filename):
        return None, (jsonify({"error": "only PDF or DOCX accepted"}), 400)

    filename = secure_filename(file.filename)
    try:
        text = extract_text(file.stream, filename)
    except Exception as e:
        return None, (jsonify({"error": f"failed to parse resume: {e}"}), 400)
    return text, None


@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# ---- i18n ----------------------------------------------------------------

@bp.route("/api/i18n/<lang>")
def i18n(lang):
    if lang not in LANG_NAMES:
        lang = "en"
    return jsonify({
        "lang": lang,
        "translations": get_translations(lang),
        "lang_names": LANG_NAMES,
    })


# ---- main analysis -------------------------------------------------------

@bp.route("/api/analyze", methods=["POST"])
def analyze_resume():
    start_time = time.time()

    resume_text, err = extract_resume_or_400()
    if err:
        return err

    jd_text = request.form.get("job_description", "").strip()
    if not jd_text:
        return jsonify({"error": "job_description is required"}), 400

    extractor = KeywordExtractor()
    resume_kw = extractor.extract(resume_text)
    jd_kw = extractor.extract(jd_text)

    scorer = ATSScorer()
    report = scorer.score(resume_text, jd_text, resume_kw, jd_kw)

    suggester = SuggestionEngine()
    report["suggestions"] = suggester.build(report, resume_text)

    matcher = JobMatcher()
    report["job_matches"] = matcher.match(resume_kw, top_n=5)

    report["processing_ms"] = int((time.time() - start_time) * 1000)
    return jsonify(report)


@bp.route("/api/job-match", methods=["POST"])
def match_jobs_only():
    start_time = time.time()

    resume_text, err = extract_resume_or_400()
    if err:
        return err

    extractor = KeywordExtractor()
    resume_kw = extractor.extract(resume_text)

    matcher = JobMatcher()
    top_matches = matcher.match(resume_kw, top_n=10)

    return jsonify({
        "matches": top_matches,
        "detected_skills": resume_kw[:30],
        "processing_ms": int((time.time() - start_time) * 1000),
    })


# ---- cover letter --------------------------------------------------------

@bp.route("/api/cover-letter", methods=["POST"])
def cover_letter():
    resume_text, err = extract_resume_or_400()
    if err:
        return err

    jd_text = request.form.get("job_description", "").strip()
    name = request.form.get("name", "").strip()
    job_title = request.form.get("job_title", "").strip()

    if not jd_text:
        return jsonify({"error": "job_description is required for the cover letter"}), 400

    result = generate_cover_letter(resume_text, jd_text, user_name=name or None,
                                   job_title=job_title or None)
    return jsonify(result)


@bp.route("/api/cover-letter/export", methods=["POST"])
def cover_letter_export():
    """same as cover-letter but returns a downloadable .docx"""
    resume_text, err = extract_resume_or_400()
    if err:
        return err

    jd_text = request.form.get("job_description", "").strip()
    name = request.form.get("name", "").strip()
    if not jd_text:
        return jsonify({"error": "job_description is required"}), 400

    result = generate_cover_letter(resume_text, jd_text, user_name=name or None)

    # build a simple docx with python-docx
    from docx import Document
    from docx.shared import Pt
    doc = Document()
    for i, para in enumerate(result["cover_letter"].split("\n\n")):
        p = doc.add_paragraph(para)
        if i == 0 and para.startswith("Dear "):
            pass
        for run in p.runs:
            run.font.size = Pt(11)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    safe_name = "".join(c for c in (name or "cover_letter") if c.isalnum() or c in " -_")
    return send_file(buf, as_attachment=True, download_name=f"{safe_name}_cover_letter.docx",
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


# ---- linkedin import -----------------------------------------------------

@bp.route("/api/linkedin/import", methods=["POST"])
def linkedin_import():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    text = data.get("text", "").strip()

    profile, error = fetch_profile(url=url or None, pasted_text=text or None)
    if error:
        return jsonify(error), 422

    resume_text = build_resume_text_from_profile(profile)
    extractor = KeywordExtractor()
    skills = extractor.extract(resume_text)

    return jsonify({
        "profile": profile,
        "skills": skills,
        "resume_text": resume_text,
    })


# ---- resume templates ----------------------------------------------------

@bp.route("/api/templates")
def templates_list():
    return jsonify({"templates": resume_templates.list_templates()})


@bp.route("/api/templates/<template_id>/export", methods=["POST"])
def template_export(template_id):
    resume_text, err = extract_resume_or_400()
    if err:
        return err

    try:
        buf = resume_templates.export_docx(resume_text, template_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return send_file(buf, as_attachment=True,
                     download_name=f"resume_{template_id}.docx",
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@bp.route("/api/templates/<template_id>/preview")
def template_preview(template_id):
    template = resume_templates.get_template(template_id)
    if not template:
        return jsonify({"error": "unknown template"}), 404
    # preview renders a small sample resume in that template's style
    return render_template("template_preview.html", template=template)


# ---- career coach --------------------------------------------------------

@bp.route("/api/coach", methods=["POST"])
def coach():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    context = data.get("context") or {}

    if not message:
        return jsonify({"error": "message is required"}), 400

    coach_instance = CareerCoach()
    # try LLM first if configured, else rule-based
    reply = coach_instance.ask_llm(message, context)
    if reply is None:
        reply, quick_questions = coach_instance.answer(message, context)
    else:
        quick_questions = ["How do I improve?", "Which jobs suit me?", "What skills should I learn?"]

    return jsonify({"reply": reply, "quick_questions": quick_questions})
