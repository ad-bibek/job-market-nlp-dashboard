"""
Generates a synthetic-but-realistic global DS/AI job postings dataset.
Used in place of live scraping for portfolio/demo purposes.
"""
import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)

ROLE_CATEGORIES = {
    "Data Analyst": {
        "titles": ["Data Analyst", "Junior Data Analyst", "Business Data Analyst", "Data Analyst II"],
        "skills": ["SQL", "Excel", "Power BI", "Tableau", "Python", "pandas", "data visualization",
                   "statistics", "A/B testing", "reporting", "data cleaning", "stakeholder communication"],
    },
    "Data Scientist": {
        "titles": ["Data Scientist", "Data Scientist II", "Applied Data Scientist", "Senior Data Scientist"],
        "skills": ["Python", "machine learning", "scikit-learn", "statistics", "SQL", "A/B testing",
                   "feature engineering", "XGBoost", "deep learning", "pandas", "experimentation"],
    },
    "Data Engineer": {
        "titles": ["Data Engineer", "Junior Data Engineer", "Senior Data Engineer", "ETL Developer"],
        "skills": ["SQL", "Python", "ETL", "Airflow", "Spark", "AWS", "Docker", "data modeling",
                   "PostgreSQL", "Redshift", "data pipelines", "Kafka"],
    },
    "ML Engineer": {
        "titles": ["Machine Learning Engineer", "ML Engineer", "Applied ML Engineer", "AI Engineer"],
        "skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "Docker", "Kubernetes", "AWS",
                   "model deployment", "deep learning", "CI/CD", "feature engineering"],
    },
    "Business Analyst": {
        "titles": ["Business Analyst", "Business Systems Analyst", "Junior Business Analyst"],
        "skills": ["SQL", "requirements gathering", "Jira", "stakeholder communication", "Excel",
                   "functional specifications", "process mapping", "UAT", "data validation", "Agile"],
    },
    "Data Quality Analyst": {
        "titles": ["Data Quality Analyst", "Data Governance Analyst", "Data Quality Specialist"],
        "skills": ["SQL", "data validation", "data profiling", "data governance", "ETL",
                   "Python", "data cleansing", "metadata management", "Excel", "reporting"],
    },
}

LOCATIONS = ["Kathmandu, Nepal", "Bengaluru, India", "Remote", "London, UK", "Berlin, Germany",
             "New York, USA", "Singapore", "Toronto, Canada", "Dublin, Ireland", "Sydney, Australia"]

COMPANIES = ["Datavantis", "Northbridge Analytics", "Clarion Health", "Meridian Labs", "Quanta Systems",
             "BrightPath AI", "Vertex Insights", "Orbit Data Co", "Lumen Analytics", "Kestrel Technologies",
             "Pinegrove Solutions", "Anchorpoint AI", "Skylark Data", "Fieldstone Group", "Havenwood Tech"]

SENIORITY = ["Entry", "Junior", "Mid", "Senior"]

DESC_TEMPLATES = [
    "We are looking for a {title} to join our growing team. You will work closely with cross-functional "
    "stakeholders to {verb1} and {verb2}. Strong hands-on experience with {skill1}, {skill2}, and {skill3} "
    "is required. Familiarity with {skill4} is a plus. This is a great opportunity to grow your career in "
    "a fast-paced, data-driven environment.",

    "{company} is hiring a {title} to support our data and analytics function. Responsibilities include "
    "{verb1}, {verb2}, and collaborating with engineering and product teams. Ideal candidates have practical "
    "experience with {skill1}, {skill2}, and {skill3}, along with a solid foundation in {skill4}.",

    "Join {company} as a {title}! In this role you'll {verb1} and {verb2} to help drive business decisions. "
    "We're looking for someone proficient in {skill1} and {skill2}, with working knowledge of {skill3}. "
    "Experience with {skill4} is preferred but not required.",

    "As a {title} at {company}, you will {verb1}, {verb2}, and partner with stakeholders across the business. "
    "Core requirements include {skill1}, {skill2}, and {skill3}. Bonus points for exposure to {skill4}.",
]

VERBS = ["analyze large datasets", "build and maintain dashboards", "design data pipelines",
         "translate business requirements into technical specifications", "validate data quality",
         "develop predictive models", "optimize database queries", "support experimentation and A/B testing",
         "automate reporting workflows", "document functional specifications", "conduct root-cause analysis",
         "partner with product and engineering teams"]


def random_date(start_days_ago=180, end_days_ago=0):
    days = random.randint(end_days_ago, start_days_ago)
    return (datetime(2026, 7, 10) - timedelta(days=days)).strftime("%Y-%m-%d")


def make_posting(posting_id):
    category = random.choice(list(ROLE_CATEGORIES.keys()))
    cat_info = ROLE_CATEGORIES[category]
    title = random.choice(cat_info["titles"])
    company = random.choice(COMPANIES)
    location = random.choice(LOCATIONS)
    seniority = random.choice(SENIORITY)
    skills = random.sample(cat_info["skills"], k=4)
    verb1, verb2 = random.sample(VERBS, k=2)
    template = random.choice(DESC_TEMPLATES)

    description = template.format(
        title=title, company=company, verb1=verb1, verb2=verb2,
        skill1=skills[0], skill2=skills[1], skill3=skills[2], skill4=skills[3],
    )

    # Intentionally inject a small % of malformed records to exercise BR-4 (data validation)
    is_malformed = random.random() < 0.06
    if is_malformed:
        malform_type = random.choice(["missing_title", "missing_description", "missing_date"])
        return {
            "posting_id": posting_id,
            "title": "" if malform_type == "missing_title" else title,
            "company": company,
            "category": category,
            "location": location,
            "seniority": seniority,
            "description": "" if malform_type == "missing_description" else description,
            "posted_date": "" if malform_type == "missing_date" else random_date(),
        }

    return {
        "posting_id": posting_id,
        "title": title,
        "company": company,
        "category": category,
        "location": location,
        "seniority": seniority,
        "description": description,
        "posted_date": random_date(),
    }


def generate(n=400):
    rows = [make_posting(i) for i in range(1, n + 1)]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate(400)
    df.to_csv("/home/claude/job_dashboard/data/postings.csv", index=False)
    print(f"Generated {len(df)} postings -> data/postings.csv")
    print(df["category"].value_counts())
    print(f"Malformed records: {(df['title']=='').sum() + (df['description']=='').sum() + (df['posted_date']=='').sum()}")
