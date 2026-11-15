
import os
import html
import hashlib
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from analyzer import (
    extract_text,
    analyze_resume,
    compare_resumes,
    format_skill
)

from resume_optimizer import optimize_resume

from resume_generator import (
    generate_pdf,
    generate_docx
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="HireLens AI 2.0",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


# ==========================================
# LOAD CSS
# ==========================================

css_path = BASE_DIR / "style.css"

if css_path.exists():
    st.html(css_path)


# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "analysis": None,
    "resume_text": "",
    "optimized_resume": "",
    "edited_resume": "",
    "input_signature": None,
    "verified_resume": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## ◈ HireLens AI")

    st.caption("Resume Intelligence Platform")

    st.divider()

    st.markdown("### AI Configuration")

    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Your key is used to connect to Gemini."
    )

    model_name = st.text_input(
        "Gemini Model",
        value=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash"
        )
    )

    if api_key:

        st.success("API key configured")

    else:

        st.info(
            "Configure an API key to enable "
            "AI resume optimization."
        )

    st.markdown(
        "[Get Gemini API Key]"
        "(https://aistudio.google.com/apikey)"
    )

    st.divider()

    st.markdown("### Features")

    st.markdown("""
    - Resume Analysis
    - Skill Gap Detection
    - AI Resume Optimization
    - Before & After Comparison
    - PDF Resume Export
    - Word Resume Export
    """)

    st.divider()

    st.caption(
        "Day 01 / 30 — 30 Days of Data & AI"
    )


# ==========================================
# FRONTEND COMPONENTS
# ==========================================

def metric_card(label, value, caption, color):

    st.html(f"""
    <div class="metric-card">

        <div class="metric-label">
            {html.escape(str(label))}
        </div>

        <div class="metric-value"
             style="color:{color};">
            {html.escape(str(value))}
        </div>

        <div class="metric-caption">
            {html.escape(str(caption))}
        </div>

    </div>
    """)


def skill_panel(title, skills, category):

    chips = "".join(
        f'<span class="skill-chip {category}">'
        f'{html.escape(format_skill(skill))}'
        f'</span>'
        for skill in sorted(skills)
    )

    if not chips:

        chips = """
        <p class="muted-text">
            No skills detected in this category.
        </p>
        """

    st.html(f"""
    <div class="skill-panel">

        <h3>{html.escape(title)}</h3>

        <div class="skills-container">
            {chips}
        </div>

    </div>
    """)


def score_circle(coverage):

    score = coverage if coverage is not None else 0

    score_display = (
        f"{coverage:.0f}%"
        if coverage is not None
        else "N/A"
    )

    st.html(f"""
    <div class="score-card">

        <div class="metric-label">
            SKILL COMPATIBILITY
        </div>

        <div class="score-ring"
             style="background:conic-gradient(
                #818cf8 0%,
                #a855f7 {score}%,
                #334155 {score}% 100%
             );">

            <div class="score-inner">

                <div class="score-number">
                    {score_display}
                </div>

                <div class="score-label">
                    SKILL MATCH
                </div>

            </div>

        </div>

        <div class="metric-caption">
            Based on detected job skills
        </div>

    </div>
    """)


def section_header(number, title, description):

    st.html(f"""
    <div class="section-header">

        <div class="section-number">
            {html.escape(number)}
        </div>

        <h2>{html.escape(title)}</h2>

        <p>{html.escape(description)}</p>

    </div>
    """)


def progress_card(label, score, color):

    width = max(0, min(100, score))

    st.html(f"""
    <div class="progress-card">

        <div class="progress-header">

            <span>{html.escape(label)}</span>

            <strong style="color:{color};">
                {score:.1f}%
            </strong>

        </div>

        <div class="progress-track">

            <div class="progress-fill"
                 style="width:{width}%;
                        background:{color};">
            </div>

        </div>

    </div>
    """)


def recommendation_card(title, description):

    st.html(f"""
    <div class="recommendation">

        <strong>
            {html.escape(title)}
        </strong>

        <p>
            {html.escape(description)}
        </p>

    </div>
    """)


def display_resume_preview(text):

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:

            lines.append(
                '<div class="resume-space"></div>'
            )

        elif line.startswith("# "):

            lines.append(
                f'<h1>{html.escape(line[2:])}</h1>'
            )

        elif line.startswith("## "):

            lines.append(
                f'<h2>{html.escape(line[3:])}</h2>'
            )

        elif line.startswith("### "):

            lines.append(
                f'<h3>{html.escape(line[4:])}</h3>'
            )

        elif line.startswith(("- ", "* ", "• ")):

            lines.append(
                '<div class="resume-bullet">'
                f'• {html.escape(line[2:])}'
                '</div>'
            )

        else:

            lines.append(
                f'<p>{html.escape(line)}</p>'
            )

    content = "".join(lines)

    st.html(f"""
    <div class="resume-paper">
        {content}
    </div>
    """)


# ==========================================
# NAVIGATION BAR
# ==========================================

st.html("""
<div class="navbar">

    <div class="logo">
        ◈ HireLens<span> AI</span>
    </div>

    <div class="nav-right">

        <span class="version-tag">
            VERSION 2.0
        </span>

        

    </div>

</div>
""")


# ==========================================
# HERO SECTION
# ==========================================

st.html("""
<div class="hero">

    <div class="hero-tag">
        ✦ AI-POWERED RESUME INTELLIGENCE
    </div>

    <h1>
        Your next opportunity<br>
        <span class="gradient-text">
            starts here.
        </span>
    </h1>

    <p>
        Discover how your resume aligns with your
        dream job. Identify skill gaps, optimize
        your resume with AI, and apply smarter.
    </p>

    <div class="hero-features">

        <span>✦ NLP Powered</span>

        <span>◈ Gemini AI</span>

        <span>✓ Skill Gap Detection</span>

        <span>↓ PDF & DOCX Export</span>

    </div>

</div>
""")


# ==========================================
# WORKFLOW INDICATOR
# ==========================================

st.html("""
<div class="workflow">

    <div class="workflow-step">

        <span class="step-icon">01</span>

        <div>
            <strong>Upload</strong>
            <small>Resume & JD</small>
        </div>

    </div>

    <div class="workflow-arrow">→</div>

    <div class="workflow-step">

        <span class="step-icon">02</span>

        <div>
            <strong>Analyze</strong>
            <small>Skill intelligence</small>
        </div>

    </div>

    <div class="workflow-arrow">→</div>

    <div class="workflow-step">

        <span class="step-icon">03</span>

        <div>
            <strong>Optimize</strong>
            <small>Generative AI</small>
        </div>

    </div>

    <div class="workflow-arrow">→</div>

    <div class="workflow-step">

        <span class="step-icon">04</span>

        <div>
            <strong>Export</strong>
            <small>PDF & Word</small>
        </div>

    </div>

</div>
""")


# ==========================================
# INPUT SECTION
# ==========================================

section_header(
    "01",
    "Let's get started",
    "Upload your existing resume and target job description."
)

left, right = st.columns(
    2,
    gap="large"
)

with left:

    st.html("""
    <div class="input-heading">
        <span class="input-icon">↥</span>
        Upload Your Resume
    </div>
    """)

    resume_file = st.file_uploader(
        "Choose your PDF resume",
        type=["pdf"]
    )

    st.caption(
        "Text-based PDF files recommended."
    )

    if resume_file is not None:

        st.success(
            f"✓ {resume_file.name} uploaded"
        )


with right:

    st.html("""
    <div class="input-heading">
        <span class="input-icon">◎</span>
        Target Job Description
    </div>
    """)

    job_description = st.text_area(
        "Paste job requirements",
        height=220,
        placeholder=(
            "Paste the complete job description "
            "of your target role here..."
        )
    )

    st.caption(
        f"{len(job_description.split())} words"
    )


# ==========================================
# RESET OLD RESULTS ON INPUT CHANGE
# ==========================================

input_signature = (
    hashlib.sha256(
        resume_file.getvalue()
    ).hexdigest()
    if resume_file is not None
    else None,
    job_description.strip()
)

if st.session_state.input_signature != input_signature:

    st.session_state.analysis = None

    st.session_state.resume_text = ""

    st.session_state.optimized_resume = ""

    st.session_state.edited_resume = ""

    st.session_state.verified_resume = None

    st.session_state.input_signature = input_signature


# ==========================================
# ANALYZE BUTTON
# ==========================================

st.write("")

analyze_clicked = st.button(
    "✦ Analyze My Resume",
    type="primary",
    use_container_width=True
)

if analyze_clicked:

    st.session_state.analysis = None

    st.session_state.optimized_resume = ""

    st.session_state.edited_resume = ""

    st.session_state.verified_resume = None

    if resume_file is None:

        st.warning(
            "Please upload your resume first."
        )

    elif not job_description.strip():

        st.warning(
            "Please enter the job description."
        )

    else:

        try:

            with st.spinner(
                "Analyzing resume and job requirements..."
            ):

                resume_file.seek(0)

                resume_text = extract_text(
                    resume_file
                )

                if not resume_text:

                    st.error(
                        "No readable text found in "
                        "the uploaded PDF."
                    )

                    st.stop()

                result = analyze_resume(
                    resume_text,
                    job_description
                )

                st.session_state.resume_text = (
                    resume_text
                )

                st.session_state.analysis = result

        except Exception as error:

            st.error(
                f"Resume analysis failed: {error}"
            )


# ==========================================
# RESULTS DASHBOARD
# ==========================================

if st.session_state.analysis is not None:

    result = st.session_state.analysis

    matched = result["matched"]

    missing = result["missing"]

    coverage = result["coverage"]

    similarity = result["similarity"]

    st.divider()

    st.html("""
    <div class="success-indicator">
        ● ANALYSIS COMPLETE
    </div>
    """)

    section_header(
        "02",
        "Your Analysis Overview",
        "Understand your resume compatibility and skill gaps."
    )


    # ======================================
    # TOP METRICS
    # ======================================

    c1, c2, c3 = st.columns(3)

    with c1:

        metric_card(
            "TEXT SIMILARITY",
            f"{similarity:.1f}%",
            "TF-IDF cosine similarity",
            "#818cf8"
        )

    with c2:

        metric_card(
            "MATCHING SKILLS",
            f"{len(matched):02d}",
            "Detected in your resume",
            "#34d399"
        )

    with c3:

        metric_card(
            "SKILL GAPS",
            f"{len(missing):02d}",
            "Skills to review",
            "#fbbf24"
        )


    # ======================================
    # SKILL COMPATIBILITY
    # ======================================

    st.write("")

    a, b = st.columns(
        [1, 2],
        gap="large"
    )

    with a:

        score_circle(coverage)

        if coverage is None:

            status = "No known job skills detected"

            status_color = "#94a3b8"

        elif coverage >= 80:

            status = "Strong Skill Coverage"

            status_color = "#34d399"

        elif coverage >= 50:

            status = "Moderate Skill Coverage"

            status_color = "#fbbf24"

        else:

            status = "Needs Improvement"

            status_color = "#fb7185"

        st.html(f"""
        <div class="status-card">

            <div class="metric-label">
                COMPATIBILITY STATUS
            </div>

            <strong style="color:{status_color};">
                {status}
            </strong>

        </div>
        """)

    with b:

        skill_panel(
            "✓ Matching Skills",
            matched,
            "matched"
        )

        st.write("")

        skill_panel(
            "⚡ Skills to Improve",
            missing,
            "missing"
        )


    # ======================================
    # OVERALL SKILL COVERAGE
    # ======================================

    if coverage is not None:

        st.write("")

        progress_card(
            "OVERALL SKILL COVERAGE",
            coverage,
            "#818cf8"
        )

        st.caption(
            f"{len(matched)} of "
            f"{len(result['job_skills'])} "
            "detected job skills matched."
        )


    # ======================================
    # SMART RECOMMENDATIONS
    # ======================================

    st.markdown(
        "### ✦ Smart Recommendations"
    )

    if coverage is None:

        recommendation = (
            "No known skills were identified in "
            "the job description. Review the "
            "requirements manually."
        )

    elif coverage >= 80:

        recommendation = (
            "Your resume covers most detected "
            "job skills. Highlight relevant projects "
            "and measurable achievements."
        )

    elif coverage >= 50:

        recommendation = (
            "Your resume has moderate skill coverage. "
            "Prioritize relevant experience and "
            "review the identified skill gaps."
        )

    else:

        recommendation = (
            "Several detected job skills are missing. "
            "Develop relevant skills and tailor "
            "your resume to the target role."
        )

    recommendation_card(
        "Personalized Insight",
        recommendation
    )

    if missing:

        recommendation_card(
            "Skills to Review",
            ", ".join(
                format_skill(skill)
                for skill in sorted(missing)
            ) + ". Only add skills you genuinely possess."
        )


    # ======================================
    # RESUME IMPROVEMENT CHECKLIST
    # ======================================

    st.html("""
    <div class="skill-panel">

        <h3>Resume Improvement Checklist</h3>

        <div class="checklist">

            <p>✓ Highlight relevant projects.</p>

            <p>✓ Use action-oriented bullet points.</p>

            <p>✓ Include verified achievements.</p>

            <p>✓ Prioritize job-relevant skills.</p>

            <p>✓ Use standard resume headings.</p>

            <p>✓ Avoid unnecessary graphics.</p>

        </div>

    </div>
    """)


    # ======================================
    # ANALYSIS REPORT
    # ======================================

    coverage_display = (
        f"{coverage:.1f}%"
        if coverage is not None
        else "N/A"
    )

    report = (
        "HIRELENS AI 2.0\n"
        "Resume Analysis Report\n"
        "================================\n\n"
        f"Text Similarity: {similarity:.1f}%\n"
        f"Skill Compatibility: {coverage_display}\n"
        f"Matching Skills: {len(matched)}\n"
        f"Skill Gaps: {len(missing)}\n\n"
        "MATCHING SKILLS:\n"
        + "\n".join(
            "- " + format_skill(s)
            for s in sorted(matched)
        )
        + "\n\nMISSING SKILLS:\n"
        + "\n".join(
            "- " + format_skill(s)
            for s in sorted(missing)
        )
        + "\n\nRECOMMENDATIONS:\n"
        + recommendation
        + "\n\nNote: These are heuristic matching "
          "metrics, not official ATS scores."
    )

    st.download_button(
        "↓ Download Analysis Report",
        data=report,
        file_name="HireLens_Analysis_Report.txt",
        mime="text/plain",
        use_container_width=True
    )

    with st.expander(
        "View Extracted Resume Text"
    ):

        st.text(
            st.session_state.resume_text
        )

    with st.expander(
        "How are the scores calculated?"
    ):

        st.markdown("""
        **Text Similarity**

        TF-IDF converts resume and job description
        text into numerical vectors. Cosine
        similarity measures their textual relevance.

        **Skill Compatibility**

        Matching detected job skills divided by
        total detected job skills, multiplied by 100.

        These metrics are not official ATS scores
        or predictions of recruitment outcomes.
        """)


    # ======================================
    # AI RESUME STUDIO
    # ======================================

    st.divider()

    st.html("""
    <div class="studio-banner">

        <div class="studio-tag">
            ✦ GENERATIVE AI
        </div>

        <h1>AI Resume Studio</h1>

        <p>
            Transform your existing resume into
            a professionally tailored resume
            for your target job.
        </p>

        <span class="powered-tag">
            Powered by Gemini
        </span>

    </div>
    """)

    section_header(
        "03",
        "Customize Your Resume",
        "Choose your preferences and generate a tailored resume."
    )

    p1, p2 = st.columns(2)

    with p1:

        target_role = st.text_input(
            "Target Job Role",
            placeholder="Example: AI/ML Engineer"
        )

    with p2:

        writing_style = st.selectbox(
            "Resume Writing Style",
            [
                "Professional",
                "Technical",
                "Concise",
                "Achievement-focused"
            ]
        )

    resume_length = st.selectbox(
        "Preferred Resume Length",
        [
            "1 Page",
            "2 Pages"
        ],
        help=(
            "The AI will target this length. "
            "Actual exported page count may vary."
        )
    )

    st.info(
        "The AI will prioritize relevant information "
        "from your existing resume. It must not "
        "invent experience, skills or achievements."
    )

    consent = st.checkbox(
        "I agree to send my resume and job description "
        "to the Gemini API for optimization."
    )

    generate_clicked = st.button(
        "✦ Generate Optimized Resume",
        type="primary",
        use_container_width=True,
        disabled=not consent
    )


    # ======================================
    # GEMINI GENERATION
    # ======================================

    if generate_clicked:

        if not api_key.strip():

            st.error(
                "Please configure your Gemini API key "
                "in the sidebar or .env file."
            )

        elif not model_name.strip():

            st.error(
                "Please enter a valid Gemini model ID."
            )

        else:

            try:

                with st.spinner(
                    "Gemini is tailoring your resume..."
                ):

                    optimized = optimize_resume(
                        resume_text=(
                            st.session_state.resume_text
                        ),
                        job_description=job_description,
                        target_role=target_role,
                        writing_style=writing_style,
                        resume_length=resume_length,
                        api_key=api_key,
                        model_name=model_name
                    )

                    st.session_state.optimized_resume = (
                        optimized
                    )

                    st.session_state.edited_resume = (
                        optimized
                    )

                    st.session_state.verified_resume = None

                st.success(
                    "Your tailored resume is ready!"
                )

            except Exception as error:

                safe_error = str(error).replace(
                    api_key,
                    "[REDACTED]"
                )

                st.error(
                    f"Resume generation failed: {safe_error}"
                )


    # ======================================
    # OPTIMIZED RESUME DASHBOARD
    # ======================================

    if st.session_state.optimized_resume:

        st.divider()

        section_header(
            "04",
            "Your Optimized Resume",
            "Review, edit and compare your tailored resume."
        )

        edit_tab, preview_tab, compare_tab = st.tabs([
            "✎ Edit Resume",
            "▤ Resume Preview",
            "↗ Score Comparison"
        ])


        # ==================================
        # EDIT RESUME
        # ==================================

        with edit_tab:

            st.caption(
                "Edit any incorrect or unnecessary "
                "information before downloading."
            )

            st.text_area(
                "Optimized Resume Content",
                key="edited_resume",
                height=600
            )

            st.caption(
                "Use # for your name, ## for section "
                "headings and - for bullet points."
            )


        # ==================================
        # PREVIEW RESUME
        # ==================================

        with preview_tab:

            display_resume_preview(
                st.session_state.edited_resume
            )


        # ==================================
        # SCORE COMPARISON
        # ==================================

        edited_text = (
            st.session_state.edited_resume.strip()
        )

        comparison = compare_resumes(
            st.session_state.resume_text,
            edited_text,
            job_description
        )

        before = comparison["before"]

        after = comparison["after"]

        with compare_tab:

            st.markdown(
                "### Before vs After Optimization"
            )

            before_col, after_col = st.columns(2)

            with before_col:

                metric_card(
                    "ORIGINAL SIMILARITY",
                    f"{before['similarity']:.1f}%",
                    "Before optimization",
                    "#fbbf24"
                )

            with after_col:

                metric_card(
                    "OPTIMIZED SIMILARITY",
                    f"{after['similarity']:.1f}%",
                    "After optimization",
                    "#34d399"
                )

            improvement = (
                after["similarity"]
                - before["similarity"]
            )

            st.metric(
                "Text Similarity Change",
                f"{improvement:+.1f} percentage points"
            )

            progress_card(
                "Original Resume",
                before["similarity"],
                "#fbbf24"
            )

            progress_card(
                "Optimized Resume",
                after["similarity"],
                "#34d399"
            )

            st.markdown(
                "### Skill Coverage Comparison"
            )

            sc1, sc2 = st.columns(2)

            before_coverage = before["coverage"]

            after_coverage = after["coverage"]

            with sc1:

                metric_card(
                    "BEFORE",
                    (
                        f"{before_coverage:.1f}%"
                        if before_coverage is not None
                        else "N/A"
                    ),
                    "Original skill coverage",
                    "#fbbf24"
                )

            with sc2:

                metric_card(
                    "AFTER",
                    (
                        f"{after_coverage:.1f}%"
                        if after_coverage is not None
                        else "N/A"
                    ),
                    "Optimized skill coverage",
                    "#34d399"
                )

            skill_panel(
                "Matching Skills After Optimization",
                after["matched"],
                "matched"
            )

            st.write("")

            skill_panel(
                "Remaining Skill Gaps",
                after["missing"],
                "missing"
            )

            st.caption(
                "Both similarity scores use the same "
                "TF-IDF vocabulary for comparison. "
                "A higher score does not guarantee "
                "ATS acceptance."
            )


        # ==================================
        # FACTUAL REVIEW
        # ==================================

        newly_detected = comparison["new_skills"]

        if newly_detected:

            st.warning(
                "Review these newly detected skills. "
                "They were not detected in the original "
                "resume: "
                + ", ".join(
                    format_skill(s)
                    for s in sorted(newly_detected)
                )
            )

        st.markdown(
            "### Final Resume Verification"
        )

        current_hash = hashlib.sha256(
            edited_text.encode("utf-8")
        ).hexdigest()

        verified = st.checkbox(
            "I have reviewed the resume and confirm "
            "that all skills, dates, qualifications "
            "and achievements are accurate.",
            key=f"verify_{current_hash}"
        )


        # ==================================
        # EXPORT SECTION
        # ==================================

        st.divider()

        section_header(
            "05",
            "Download Your Resume",
            "Export your verified resume in a clean, single-column format."
        )

        if verified and edited_text:

            try:
                pdf_data = generate_pdf(edited_text,
                                        resume_length
)

                docx_data = generate_docx(
                edited_text,
                resume_length
)

                
                
                

                d1, d2 = st.columns(2)

                with d1:

                    st.download_button(
                        "↓ Download PDF Resume",
                        data=pdf_data,
                        file_name=(
                            "HireLens_Optimized_Resume.pdf"
                        ),
                        mime="application/pdf",
                        use_container_width=True
                    )

                with d2:

                    st.download_button(
                        "↓ Download Word Resume",
                        data=docx_data,
                        file_name=(
                            "HireLens_Optimized_Resume.docx"
                        ),
                        mime=(
                            "application/vnd.openxmlformats-"
                            "officedocument.wordprocessingml."
                            "document"
                        ),
                        use_container_width=True
                    )

                st.download_button(
                    "↓ Download Resume Text",
                    data=edited_text,
                    file_name="Optimized_Resume.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except Exception as error:

                st.error(
                    f"Resume export failed: {error}"
                )

        else:

            st.info(
                "Review your resume and complete the "
                "verification checkbox to enable downloads."
            )


# ==========================================
# EMPTY STATE
# ==========================================

else:

    st.html("""
    <div class="empty-state">

        <div class="empty-icon">
            ◈
        </div>

        <h3>Your insights will appear here</h3>

        <p>
            Upload your resume and enter a job
            description to get started.
        </p>

    </div>
    """)


# ==========================================
# FOOTER
# ==========================================

st.html("""
<div class="footer">

    <div class="footer-logo">
        ◈ HireLens <span>AI</span>
    </div>

    <p>
        Intelligent Resume Analyzer,
        Optimizer & Builder
    </p>

    <p>
        Designed & Developed by
        <strong>Riya Rathore</strong>
    </p>


    <p class="footer-tech">
        Python · NLP · Gemini · Scikit-learn · Streamlit
    </p>

</div>
""")
