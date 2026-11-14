# Resume Parser 

# importin libraries and client creation 

import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel


load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
  raise ValueError("Invalid Api Key")

client = Groq(api_key=my_api_key)

model = "openai/gpt-oss-20b"

# job description 

class JobD(BaseModel):
  role:str
  required_skills:list[str]
  preferred_skills:list[str]
  minimum_exp:int
  educational_requirements:list[str]
  responsibilities:list[str]

schema = JobD.model_json_schema()
response_format = {
  "type":"json_object"
}

system_prompt = f"""
You are an expert technical recruiter.

Extract the job requirements from the supplied job description.

Return a JSON object following this schema:

{schema}

Return valid JSON only.
"""

message_system = {
  "role":"system",
  "content":system_prompt
}

Job_Description = f"""# Job Description: Junior AI/ML Engineer

**Job Title:** Junior AI/ML Engineer  
**Department:** Artificial Intelligence & Machine Learning  
**Experience:** 0-2 Years  
**Employment Type:** Full-time  
**Location:** Bangalore, India

## About the Role

We are looking for a motivated Junior AI/ML Engineer to join our engineering team. The ideal candidate should have a strong foundation in Python programming, machine learning, deep learning, and an interest in developing practical AI-powered applications.

You will work alongside experienced engineers to develop, train, evaluate, and deploy machine learning models and integrate Large Language Models (LLMs) into real-world applications.

## Responsibilities

- Develop and implement machine learning models using Python.
- Perform data preprocessing, cleaning, and exploratory data analysis.
- Work with machine learning frameworks such as Scikit-learn, TensorFlow, or PyTorch.
- Develop deep learning applications using neural networks.
- Explore and integrate Large Language Models (LLMs) into applications.
- Build Retrieval-Augmented Generation (RAG) pipelines.
- Work with APIs and backend frameworks such as FastAPI.
- Collaborate with software engineers and data scientists.
- Evaluate model performance and optimize model accuracy.
- Write clean, maintainable, and well-documented code.

## Required Technical Skills

**Programming**
- Python
- Object-Oriented Programming
- Data Structures and Algorithms

**Machine Learning**
- Supervised and Unsupervised Learning
- Regression and Classification
- Decision Trees and Random Forest
- Model Evaluation and Validation

**Deep Learning**
- Artificial Neural Networks
- CNN and RNN fundamentals
- Transformers and Attention Mechanisms

**Frameworks and Libraries**
- NumPy
- Pandas
- Scikit-learn
- PyTorch or TensorFlow

**Generative AI**
- LLM fundamentals
- Prompt Engineering
- LangChain or LlamaIndex
- RAG architecture
- Vector Databases

**Backend and Development**
- FastAPI or Flask
- REST APIs
- SQL fundamentals
- Git and GitHub

## Preferred Qualifications

- Bachelor's or Master's degree in Computer Science, Information Technology, Mathematics, Data Science, or a related discipline.
- Experience developing machine learning or AI projects.
- Familiarity with cloud platforms such as AWS, Azure, or GCP.
- Familiarity with Docker and containerization.
- Understanding of model deployment and inference optimization.

## Soft Skills

- Analytical and problem-solving abilities.
- Strong communication skills.
- Ability to work collaboratively.
- Willingness to learn new technologies.
- Attention to detail.

## What We Offer

- Opportunity to work on real-world AI applications.
- Mentorship from experienced AI engineers.
- Exposure to modern LLM and machine learning technologies.
- Professional development opportunities.
- Competitive compensation based on skills and experience.

## Application Requirements

Candidates should submit:
- Updated resume.
- GitHub profile (if available).
- Portfolio or links to relevant projects (if available)."""

user_prompt = f"""Ananlyze the job description from the {Job_Description}"""


message_user = {
  "role":"user",
  "content":user_prompt
}

messages = [message_system,message_user]

response = client.chat.completions.create(model=model,messages=messages,response_format=response_format)
answer = response.choices[0].message.content

import json

raw_json = answer
data_file = json.loads(raw_json)


class Resume(BaseModel):
    name: str
    email: str
    phone: str
    education: str
    experience: str
    skills: list[str]
    projects: list[str]

resume_schema = Resume.model_json_schema()


from docx import Document


def read_resume(file_path: str) -> str:
    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)

def read_all_resumes(folder_path: str) -> dict:
    resumes = {}

    for file_path in Path(folder_path).glob("*.docx"):
        resumes[file_path.name] = read_resume(file_path)

    return resumes


from typing import Literal

# evaluation of the resumes 

class CriterionMatch(BaseModel):
    requirement: str
    status: Literal["matched", "partial", "missing", "insufficient_evidence"]
    evidence: str


class ResumeEvaluation(BaseModel):
    candidate_name: str
    required_skills: list[CriterionMatch]
    preferred_skills: list[CriterionMatch]
    experience: CriterionMatch
    education: CriterionMatch
    strengths: list[str]
    gaps: list[str]

evaluation_schema = ResumeEvaluation.model_json_schema()

def calculate_match_score(evaluation: ResumeEvaluation):

    points = {
        "matched": 1,
        "partial": 0.5,
        "missing": 0,
        "insufficient_evidence": 0
    }

    required = evaluation.required_skills
    preferred = evaluation.preferred_skills

    required_score = (
        sum(points[item.status] for item in required) / len(required)
        if required else None
    )

    preferred_score = (
        sum(points[item.status] for item in preferred) / len(preferred)
        if preferred else None
    )

    experience_score = points[evaluation.experience.status]
    education_score = points[evaluation.education.status]

    weighted_score = 0
    total_weight = 0

    components = [
        (required_score, 70),
        (preferred_score, 5),
        (experience_score, 15),
        (education_score, 10)
    ]

    for score, weight in components:
        if score is not None:
            weighted_score += score * weight
            total_weight += weight

    return round((weighted_score / total_weight) * 100, 2)


system_prompt_evaluator = f"""
You are an experienced technical recruiter.

Your task is to evaluate ONE candidate's resume
against the supplied job requirements.

Follow this JSON schema exactly:

{evaluation_schema}

Rules:
1. Evaluate every required skill individually.
2. Evaluate every preferred skill individually.
3. Use only evidence found in the resume.
4. Never invent skills or qualifications.
5. Distinguish missing from insufficient evidence.
6. Do not treat academic projects as professional experience.
7. Return valid JSON only.
"""

# Convert job description into structured data
job_requirements = json.dumps(data_file)


all_resumes = read_all_resumes("./resumes")

for filename, candidate_resume in all_resumes.items():

    print(f"\nEvaluating: {filename}")

    messages = [
        {
            "role": "system",
            "content": system_prompt_evaluator
        },
        {
            "role": "user",
            "content": f"""
            JOB REQUIREMENTS:
            {job_requirements}

            CANDIDATE RESUME:
            {candidate_resume}

            Evaluate this candidate against the requirements.
            """
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )

    answer = response.choices[0].message.content

    evaluation = ResumeEvaluation.model_validate_json(answer)

    score = calculate_match_score(evaluation)

    print(f"Candidate: {evaluation.candidate_name}")
    print(f"Match Percentage: {score}%")

    print(evaluation.model_dump_json(indent=2))
