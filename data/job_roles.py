# job roles database
# each role has a name, required skills (must-have), and preferred skills (nice-to-have)
# score = full points for required matches + half points for preferred matches
# added common roles a student/fresher might apply for

JOB_ROLES = [
    {
        "title": "Backend Developer (Java/Spring Boot)",
        "category": "Backend",
        "required": ["java", "spring boot", "rest api", "mysql", "oop"],
        "preferred": ["hibernate", "junit", "microservices", "docker", "git", "agile", "postman"],
        "description": "Build server-side apps with Spring Boot, JPA, and MySQL. Great for CS students who like Java.",
    },
    {
        "title": "Backend Developer (Python/Flask)",
        "category": "Backend",
        "required": ["python", "flask", "rest api", "sql"],
        "preferred": ["django", "fastapi", "mysql", "postgresql", "docker", "git", "pytest"],
        "description": "Build APIs and services with Python. Common at startups and data-heavy companies.",
    },
    {
        "title": "Full Stack Developer",
        "category": "Full Stack",
        "required": ["javascript", "html", "css", "rest api"],
        "preferred": ["react", "node.js", "express", "mongodb", "python", "flask", "git", "typescript"],
        "description": "Work on both frontend and backend. High-demand role for portfolio-heavy students.",
    },
    {
        "title": "Frontend Developer",
        "category": "Frontend",
        "required": ["javascript", "html", "css"],
        "preferred": ["react", "typescript", "redux", "tailwind", "git", "next.js", "vue"],
        "description": "Build interactive user interfaces with React/Vue. Focus on UX and performance.",
    },
    {
        "title": "Data Analyst",
        "category": "Data",
        "required": ["python", "sql", "pandas"],
        "preferred": ["numpy", "matplotlib", "excel", "tableau", "power bi", "statistics"],
        "description": "Turn data into insights using Python, SQL, and visualization tools.",
    },
    {
        "title": "Data Scientist / ML Engineer",
        "category": "Data",
        "required": ["python", "machine learning", "pandas", "scikit-learn"],
        "preferred": ["numpy", "tensorflow", "pytorch", "nlp", "sql", "deep learning", "statistics"],
        "description": "Build ML models. Strong Python + math fundamentals required.",
    },
    {
        "title": "NLP / AI Engineer",
        "category": "AI/ML",
        "required": ["python", "nlp", "machine learning"],
        "preferred": ["scikit-learn", "tensorflow", "pytorch", "llm", "tokenization", "tf-idf", "cosine similarity"],
        "description": "Work on language models, chatbots, text analysis. Growing field with high demand.",
    },
    {
        "title": "DevOps / SRE Intern",
        "category": "DevOps",
        "required": ["docker", "git", "linux"],
        "preferred": ["kubernetes", "aws", "ci/cd", "jenkins", "terraform", "python", "monitoring"],
        "description": "Deploy and monitor apps at scale. Cloud + automation focused.",
    },
    {
        "title": "Cloud Engineer (AWS)",
        "category": "Cloud",
        "required": ["aws", "linux"],
        "preferred": ["ec2", "s3", "lambda", "cloudfront", "docker", "kubernetes", "terraform", "python"],
        "description": "Design and manage AWS-based infrastructure. Cert-friendly path.",
    },
    {
        "title": "Software Engineer Intern (Generalist)",
        "category": "General",
        "required": ["data structures", "algorithms", "oop"],
        "preferred": ["java", "python", "c++", "git", "sql", "rest api", "agile"],
        "description": "Broad SDE role. DSA + one strong language matters most.",
    },
    {
        "title": "Database Administrator / SQL Developer",
        "category": "Database",
        "required": ["sql", "mysql"],
        "preferred": ["postgresql", "mongodb", "dbms", "python", "data structures", "redis"],
        "description": "Design schemas, optimize queries, handle production DBs.",
    },
    {
        "title": "QA / Test Automation Engineer",
        "category": "QA",
        "required": ["git"],
        "preferred": ["selenium", "junit", "pytest", "java", "python", "postman", "rest api", "agile"],
        "description": "Automate testing pipelines. Good entry route for CS grads.",
    },
]
