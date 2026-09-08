# LinkedIn profile import
# fetches a public LinkedIn profile and tries to extract name/headline/skills/education
# NOTE: LinkedIn blocks most automated requests (returns 999), so this is best-effort.
# If the request is blocked, we return a clean error and the user can paste
# their profile text manually through the same endpoint.

import re

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_profile(url=None, pasted_text=None):
    """
    try to build a profile dict from either a LinkedIn URL or pasted profile text
    """
    if pasted_text and pasted_text.strip():
        return extract_from_text(pasted_text)

    if not url or "linkedin.com" not in url:
        return None, {"error": "please paste a valid LinkedIn profile URL or your profile text"}

    # normalize the url: public profiles usually are /in/<username>
    m = re.search(r"linkedin\.com/in/([A-Za-z0-9\-_]+)", url)
    if m:
        username = m.group(1)
    else:
        username = None

    try:
        resp = requests.get(url.strip(), headers=HEADERS, timeout=12)
    except requests.RequestException as e:
        return None, {"error": f"network error while fetching profile: {e}"}

    # LinkedIn returns 999 when it detects automation
    if resp.status_code != 200:
        hint = ""
        if username:
            hint = (
                f"LinkedIn blocked automated access (status {resp.status_code}). "
                f"Try opening your profile in a browser and pasting the page text "
                f"into the 'paste profile text' box instead."
            )
        else:
            hint = (
                f"Could not fetch the profile (status {resp.status_code}). "
                "Paste your profile text manually instead."
            )
        return None, {"error": hint}

    return extract_from_text(resp.text)


def extract_from_text(text):
    """regex-based extraction from raw profile page or pasted profile text"""
    profile = {"name": None, "headline": None, "skills": [], "education": None}

    # name: usually <title>Name - Title | LinkedIn</title> or og:title meta
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    if title:
        clean = re.sub(r"\s+", " ", title.group(1)).strip()
        clean = re.sub(r"\s*\|\s*LinkedIn.*$", "", clean)
        if clean and "linkedin" not in clean.lower():
            profile["name"] = clean

    og = re.search(r'property="og:title"\s+content="([^"]+)"', text)
    if og and not profile["name"]:
        profile["name"] = og.group(1).split("|")[0].strip()

    desc = re.search(r'name="description"\s+content="([^"]+)"', text)
    if desc and not profile["headline"]:
        profile["headline"] = desc.group(1)[:150]

    # skills: look for lines in a "Skills" section (works for pasted text)
    in_skills = False
    skill_rx = re.compile(r"^[A-Z][A-Za-z0-9+.#&\- ]{2,40}$")
    for line in text.splitlines():
        stripped = line.strip()
        if re.search(r"(skills|expertise)", stripped, re.I):
            in_skills = True
            continue
        if in_skills:
            if re.search(r"(education|experience|projects|certifications|contact|activity)", stripped, re.I):
                break
            if 2 <= len(stripped) <= 45 and skill_rx.match(stripped):
                profile["skills"].append(stripped)
        if len(profile["skills"]) >= 15:
            break

    edu = re.search(r"(B\.?Tech|Bachelor|Master|MBA)[^,|\n]{0,60}", text, re.I)
    if edu:
        profile["education"] = edu.group(0).strip()

    return profile, None


def build_resume_text_from_profile(profile):
    """turns an extracted profile into plain resume-ish text we can analyze"""
    lines = []
    if profile.get("name"):
        lines.append(profile["name"])
    if profile.get("headline"):
        lines.append(profile["headline"])
    if profile.get("education"):
        lines.append("EDUCATION: " + profile["education"])
    if profile.get("skills"):
        lines.append("SKILLS: " + ", ".join(profile["skills"]))
    return "\n".join(lines)
