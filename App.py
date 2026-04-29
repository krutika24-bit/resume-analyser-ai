import streamlit as st
import os
import json
import re
from pathlib import Path
import anthropic

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyser AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Dark background */
.stApp {
    background: #0d0d0d;
    color: #e8e8e8;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid #222;
}

/* Score card */
.score-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    margin-bottom: 16px;
}
.score-number {
    font-size: 64px;
    font-weight: 700;
    background: linear-gradient(90deg, #e94560, #0f3460);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.score-label {
    font-size: 13px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 6px;
}

/* Section cards */
.section-card {
    background: #111;
    border: 1px solid #222;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}
.section-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #e94560;
    margin-bottom: 12px;
}

/* Skill tags */
.skill-tag {
    display: inline-block;
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: #c8f7c5;
    margin: 3px;
}
.skill-missing {
    border-color: #e94560;
    color: #f7a8b4;
}

/* Progress bar override */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #e94560, #533483);
}

/* Header */
.main-header {
    background: linear-gradient(135deg, #0d0d0d 0%, #1a0a2e 100%);
    padding: 32px 0 20px;
    margin-bottom: 8px;
}

/* File uploader styling */
[data-testid="stFileUploader"] {
    background: #111;
    border: 2px dashed #333;
    border-radius: 12px;
    padding: 8px;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #e94560, #533483);
    color: white;
    border: none;
    border-radius: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 15px;
    padding: 12px 32px;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover {
    opacity: 0.85;
}

/* Divider */
hr {
    border-color: #222;
}

/* Text area */
.stTextArea textarea {
    background: #111;
    border: 1px solid #333;
    color: #e8e8e8;
    border-radius: 10px;
    font-family: 'Space Grotesk', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    import pypdf, io
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX."""
    import docx, io
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs)


def analyse_resume(resume_text: str, job_description: str, api_key: str) -> dict:
    """Call Claude API and parse structured JSON response."""
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = """You are an expert resume reviewer and ATS (Applicant Tracking System) specialist.
Analyse the resume against the job description and return ONLY a valid JSON object.
No markdown, no preamble, no trailing text — pure JSON only.

JSON schema:
{
  "overall_score": <int 0-100>,
  "ats_score": <int 0-100>,
  "summary": "<2-3 sentence overview>",
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "weaknesses": ["<weakness 1>", "<weakness 2>", ...],
  "matched_skills": ["skill1", "skill2", ...],
  "missing_skills": ["skill1", "skill2", ...],
  "experience_analysis": "<paragraph>",
  "education_analysis": "<paragraph>",
  "formatting_tips": ["<tip 1>", "<tip 2>", ...],
  "action_items": ["<action 1>", "<action 2>", ...],
  "keyword_density": <int 0-100>,
  "sections_found": ["Contact", "Experience", "Education", ...],
  "sections_missing": ["Summary", "Projects", ...]
}"""

    user_msg = f"""RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description if job_description.strip() else "No job description provided. Perform a general resume analysis."}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = message.content[0].text.strip()
    # Strip possible markdown fences
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def score_color(score: int) -> str:
    if score >= 80:
        return "#4ade80"
    elif score >= 60:
        return "#facc15"
    else:
        return "#e94560"


def render_score_card(label: str, score: int):
    color = score_color(score)
    st.markdown(f"""
    <div class="score-card">
        <div style="font-size:52px;font-weight:700;color:{color};line-height:1">{score}</div>
        <div class="score-label">{label}</div>
    </div>""", unsafe_allow_html=True)
    st.progress(score / 100)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key from console.anthropic.com",
    )
    st.divider()
    st.markdown("### 📁 Upload Resume")
    uploaded_file = st.file_uploader(
        "PDF or DOCX",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("### 🎯 Job Description *(optional)*")
    job_desc = st.text_area(
        "Paste the job posting here for a targeted analysis",
        height=200,
        label_visibility="collapsed",
        placeholder="Paste the job description here...",
    )
    st.divider()
    analyse_btn = st.button("🔍 Analyse Resume", use_container_width=True)
    st.markdown("""
    <div style="font-size:11px;color:#555;margin-top:16px;line-height:1.6">
    Powered by <strong>Claude claude-sonnet-4-20250514</strong><br>
    Your resume is never stored.
    </div>""", unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="font-size:38px;font-weight:700;margin:0">
        📄 Resume <span style="color:#e94560">Analyser</span> AI
    </h1>
    <p style="color:#666;margin:6px 0 0;font-size:15px">
        ATS scoring · skills gap · actionable feedback — powered by Claude
    </p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# ── Run analysis ──────────────────────────────────────────────────────────────
if analyse_btn:
    if not api_key:
        st.error("⚠️  Please enter your Anthropic API key in the sidebar.")
    elif not uploaded_file:
        st.error("⚠️  Please upload a resume (PDF, DOCX, or TXT).")
    else:
        file_bytes = uploaded_file.read()
        ext = Path(uploaded_file.name).suffix.lower()

        with st.spinner("Reading resume…"):
            if ext == ".pdf":
                resume_text = extract_text_from_pdf(file_bytes)
            elif ext == ".docx":
                resume_text = extract_text_from_docx(file_bytes)
            else:
                resume_text = file_bytes.decode("utf-8", errors="ignore")

        if len(resume_text.strip()) < 50:
            st.error("Could not extract enough text from the file. Try a different format.")
        else:
            st.session_state.resume_text = resume_text
            with st.spinner("Analysing with Claude AI… this takes ~10 seconds"):
                try:
                    st.session_state.result = analyse_resume(resume_text, job_desc, api_key)
                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse AI response as JSON: {e}")
                    st.session_state.result = None
                except Exception as e:
                    st.error(f"API error: {e}")
                    st.session_state.result = None

# ── Display results ───────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Scores row
    col1, col2, col3 = st.columns(3)
    with col1:
        render_score_card("Overall Score", r.get("overall_score", 0))
    with col2:
        render_score_card("ATS Compatibility", r.get("ats_score", 0))
    with col3:
        render_score_card("Keyword Density", r.get("keyword_density", 0))

    st.divider()

    # Summary
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">📝 Summary</div>
        <p style="color:#ccc;line-height:1.7;margin:0">{r.get("summary","")}</p>
    </div>""", unsafe_allow_html=True)

    # Two-column layout
    left, right = st.columns(2)

    with left:
        # Strengths
        strengths_html = "".join(f"<li style='margin:6px 0;color:#ccc'>{s}</li>" for s in r.get("strengths", []))
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">✅ Strengths</div>
            <ul style="padding-left:18px;margin:0">{strengths_html}</ul>
        </div>""", unsafe_allow_html=True)

        # Matched Skills
        skill_tags = "".join(f'<span class="skill-tag">{s}</span>' for s in r.get("matched_skills", []))
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🎯 Matched Skills</div>
            <div>{skill_tags if skill_tags else "<span style='color:#555'>None detected</span>"}</div>
        </div>""", unsafe_allow_html=True)

        # Sections found / missing
        found = "  ".join(f'<span class="skill-tag">{s}</span>' for s in r.get("sections_found", []))
        missing = "  ".join(f'<span class="skill-tag skill-missing">{s}</span>' for s in r.get("sections_missing", []))
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">📑 Resume Sections</div>
            <div style="margin-bottom:8px">{found}</div>
            <div style="font-size:11px;color:#666;margin:6px 0 4px">MISSING</div>
            <div>{missing if missing else "<span style='color:#4ade80;font-size:13px'>All key sections present ✓</span>"}</div>
        </div>""", unsafe_allow_html=True)

    with right:
        # Weaknesses
        weak_html = "".join(f"<li style='margin:6px 0;color:#ccc'>{w}</li>" for w in r.get("weaknesses", []))
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">⚠️ Areas to Improve</div>
            <ul style="padding-left:18px;margin:0">{weak_html}</ul>
        </div>""", unsafe_allow_html=True)

        # Missing Skills
        miss_tags = "".join(f'<span class="skill-tag skill-missing">{s}</span>' for s in r.get("missing_skills", []))
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">❌ Missing Skills</div>
            <div>{miss_tags if miss_tags else "<span style='color:#4ade80;font-size:13px'>No gaps found ✓</span>"}</div>
        </div>""", unsafe_allow_html=True)

        # Formatting Tips
        fmt_html = "".join(f"<li style='margin:6px 0;color:#ccc'>{t}</li>" for t in r.get("formatting_tips", []))
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🎨 Formatting Tips</div>
            <ul style="padding-left:18px;margin:0">{fmt_html}</ul>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Experience & Education
    exp_col, edu_col = st.columns(2)
    with exp_col:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">💼 Experience Analysis</div>
            <p style="color:#ccc;line-height:1.7;margin:0">{r.get("experience_analysis","")}</p>
        </div>""", unsafe_allow_html=True)

    with edu_col:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🎓 Education Analysis</div>
            <p style="color:#ccc;line-height:1.7;margin:0">{r.get("education_analysis","")}</p>
        </div>""", unsafe_allow_html=True)

    # Action Items
    actions_html = "".join(
        f"""<div style="display:flex;align-items:flex-start;gap:10px;margin:10px 0">
            <span style="color:#e94560;font-weight:700;font-size:16px;min-width:20px">{i+1}.</span>
            <span style="color:#ccc;line-height:1.6">{a}</span>
        </div>"""
        for i, a in enumerate(r.get("action_items", []))
    )
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">🚀 Action Items</div>
        {actions_html}
    </div>""", unsafe_allow_html=True)

    # Raw resume preview expander
    with st.expander("📃 View extracted resume text"):
        st.text_area("", st.session_state.resume_text, height=300, label_visibility="collapsed")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;margin-top:40px;border-top:1px solid #1e1e1e">
    <span style="font-size:13px;color:#444">Built with ❤️ by </span>
    <span style="font-size:14px;font-weight:600;background:linear-gradient(90deg,#e94560,#533483);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent">Krutika Bhoi</span>
</div>
""", unsafe_allow_html=True)

else:
    # Welcome / empty state
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#444">
        <div style="font-size:72px;margin-bottom:16px">📄</div>
        <div style="font-size:22px;font-weight:600;color:#666;margin-bottom:8px">No resume analysed yet</div>
        <div style="font-size:14px;color:#444;line-height:1.8;max-width:400px;margin:0 auto">
            Upload your resume (PDF, DOCX, or TXT) in the sidebar,<br>
            optionally paste a job description,<br>
            then click <strong style="color:#e94560">Analyse Resume</strong>.
        </div>
    </div>""", unsafe_allow_html=True)

    # Feature cards
    f1, f2, f3 = st.columns(3)
    for col, icon, title, desc in [
        (f1, "🎯", "ATS Scoring", "Check how well your resume passes Applicant Tracking Systems"),
        (f2, "🔍", "Skills Gap", "See matched and missing skills vs a job description"),
        (f3, "🚀", "Action Items", "Get a prioritised to-do list to improve your resume"),
    ]:
        with col:
            st.markdown(f"""
            <div class="section-card" style="text-align:center;padding:28px 16px">
                <div style="font-size:36px;margin-bottom:10px">{icon}</div>
                <div style="font-weight:600;font-size:15px;margin-bottom:6px;color:#ddd">{title}</div>
                <div style="font-size:13px;color:#666;line-height:1.6">{desc}</div>
            </div>""", unsafe_allow_html=True)
