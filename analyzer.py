
import re

from pypdf import PdfReader

from sklearn.feature_extraction.text import (
    TfidfVectorizer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)


# ==========================================
# TECHNICAL SKILLS DATABASE
# ==========================================

SKILLS = [
    "python", "java", "c++", "c#",
    "javascript", "typescript", "sql",
    "mysql", "postgresql", "mongodb",
    "sql server", "excel", "power bi",
    "tableau", "pandas", "numpy",
    "matplotlib", "seaborn", "machine learning",
    "deep learning", "artificial intelligence",
    "data analysis", "data science", "nlp",
    "computer vision", "tensorflow", "pytorch",
    "scikit-learn", "flask", "django", "fastapi",
    "react", "next.js", "html", "css", "node.js",
    "docker", "kubernetes", "aws", "azure",
    "git", "github", "rest api", "hadoop",
    "spark", "kafka", "langchain", "langgraph",
    "rag", "llm", "generative ai", "faiss",
    "statistics", "data visualization",
    "feature engineering", "data cleaning",
    "linux", "agile", "streamlit", "opencv",
    "communication", "problem solving",
    "transformers", "hugging face",
    "prompt engineering", "api development",
    "data engineering", "etl", "snowflake",
    "redis", "graphql", "firebase",
    "data structures", "algorithms",
    "software development", "testing",
    "ci/cd", "jenkins", "gitlab",
    "gcp", "xgboost", "lightgbm",
    "beautifulsoup", "selenium",
    "reinforcement learning", "neural networks",
    "classification", "regression", "clustering",
    "time series", "forecasting",
    "business intelligence", "data modeling",
    "data warehousing", "big data",
    "microservices", "system design",
    "object oriented programming",
    "backend development", "frontend development",
    "full stack development", "unit testing",
    "pytest", "postman", "jira",
    "spring boot", "angular", "bootstrap",
    "tailwind css", "figma", "typescript",
    "sqlalchemy", "alembic", "websockets",
    "gemini", "openai", "vector database",
    "embeddings", "pyspark", "databricks",
    "mlflow", "mlops", "airflow",
    "data preprocessing", "model deployment",
    "model evaluation", "web scraping",
    "power query", "dax", "vlookup",
    "pivot tables", "data mining",
    "business analysis", "dashboard development"
]


# ==========================================
# SKILL ALIASES
# ==========================================

ALIASES = {
    "natural language processing": "nlp",
    "large language models": "llm",
    "large language model": "llm",
    "llms": "llm",
    "retrieval augmented generation": "rag",
    "retrieval-augmented generation": "rag",
    "generative artificial intelligence": "generative ai",
    "gen ai": "generative ai",
    "genai": "generative ai",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "restful api": "rest api",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "powerbi": "power bi",
    "problem-solving": "problem solving",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "object-oriented programming": (
        "object oriented programming"
    ),
    "oop": "object oriented programming",
    "postgres": "postgresql",
    "nodejs": "node.js",
    "nextjs": "next.js",
    "reactjs": "react",
    "microsoft excel": "excel"
}


# ==========================================
# PDF EXTRACTION
# ==========================================

def extract_text(file):

    reader = PdfReader(file)

    if reader.is_encrypted:

        if not reader.decrypt(""):

            raise ValueError(
                "Please upload an unlocked PDF."
            )

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    return text.strip()


# ==========================================
# TEXT NORMALIZATION
# ==========================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    for old, new in sorted(
        ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        text = re.sub(
            r"(?<!\w)"
            + re.escape(old)
            + r"(?!\w)",
            new,
            text
        )

    return text.strip()


# ==========================================
# SKILL EXTRACTION
# ==========================================

def extract_skills(text):

    normalized = normalize_text(text)

    found = set()

    for skill in SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            normalized
        ):

            found.add(skill)

    return found


# ==========================================
# TF-IDF SIMILARITY
# ==========================================

def calculate_similarity(
    resume_text,
    job_description
):

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    try:

        vectors = vectorizer.fit_transform([
            normalize_text(resume_text),
            normalize_text(job_description)
        ])

        score = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(
            float(score) * 100,
            2
        )

    except ValueError:

        return 0.0


# ==========================================
# COMPLETE RESUME ANALYSIS
# ==========================================

def analyze_resume(
    resume_text,
    job_description
):

    resume_skills = extract_skills(
        resume_text
    )

    job_skills = extract_skills(
        job_description
    )

    matched = (
        resume_skills & job_skills
    )

    missing = (
        job_skills - resume_skills
    )

    similarity = calculate_similarity(
        resume_text,
        job_description
    )

    coverage = (
        round(
            len(matched)
            / len(job_skills)
            * 100,
            1
        )
        if job_skills
        else None
    )

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched": matched,
        "missing": missing,
        "similarity": similarity,
        "coverage": coverage
    }


# ==========================================
# BEFORE-AFTER COMPARISON
# ==========================================

def compare_resumes(
    original_resume,
    optimized_resume,
    job_description
):

    before = analyze_resume(
        original_resume,
        job_description
    )

    after = analyze_resume(
        optimized_resume,
        job_description
    )

    # Use the same TF-IDF feature space
    # for both resume similarity scores.

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    try:

        vectors = vectorizer.fit_transform([
            normalize_text(original_resume),
            normalize_text(optimized_resume),
            normalize_text(job_description)
        ])

        before["similarity"] = round(
            float(
                cosine_similarity(
                    vectors[0:1],
                    vectors[2:3]
                )[0][0]
            ) * 100,
            2
        )

        after["similarity"] = round(
            float(
                cosine_similarity(
                    vectors[1:2],
                    vectors[2:3]
                )[0][0]
            ) * 100,
            2
        )

    except ValueError:

        before["similarity"] = 0.0

        after["similarity"] = 0.0

    new_skills = (
        after["resume_skills"]
        - before["resume_skills"]
    )

    return {
        "before": before,
        "after": after,
        "new_skills": new_skills
    }


# ==========================================
# PROFESSIONAL SKILL FORMATTING
# ==========================================

def format_skill(skill):

    special_names = {
        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "mongodb": "MongoDB",
        "nlp": "NLP",
        "llm": "LLM",
        "rag": "RAG",
        "aws": "AWS",
        "gcp": "GCP",
        "etl": "ETL",
        "html": "HTML",
        "css": "CSS",
        "ci/cd": "CI/CD",
        "faiss": "FAISS",
        "opencv": "OpenCV",
        "fastapi": "FastAPI",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "numpy": "NumPy",
        "github": "GitHub",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "power bi": "Power BI",
        "langchain": "LangChain",
        "langgraph": "LangGraph",
        "scikit-learn": "Scikit-learn",
        "rest api": "REST API",
        "next.js": "Next.js",
        "node.js": "Node.js",
        "c++": "C++",
        "c#": "C#",
        "mlops": "MLOps",
        "mlflow": "MLflow",
        "pyspark": "PySpark",
        "openai": "OpenAI",
        "generative ai": "Generative AI",
        "sqlalchemy": "SQLAlchemy",
        "xgboost": "XGBoost",
        "lightgbm": "LightGBM",
        "dax": "DAX",
        "vlookup": "VLOOKUP"
    }

    return special_names.get(
        skill,
        skill.title()
    )
