import json
import ollama

with open("jd.txt", "r", encoding="utf-8") as f:
    jd = f.read()

with open("my_skills.txt", "r", encoding="utf-8") as f:
    my_skills = [line.strip() for line in f if line.strip()]

print("Reading job description...\n")

# Step 1: AI only extracts the skills from the job description
response = ollama.chat(
    model="llama3.2",
    messages=[{
        "role": "user",
        "content": f"""List only the specific technologies, programming languages, frameworks, tools and technical skills required in this job description.
Do NOT include company product names, business areas, team names or vague phrases.
Include AI/ML skills such as LLMs, RAG, machine learning and cloud services, and include API and backend skills.
Return ONLY JSON in this format: {{"skills": ["skill1", "skill2"]}}

Job description:
{jd}"""
    }],
    format="json",
    options={"temperature": 0},
)
job_skills = json.loads(response["message"]["content"])["skills"]

# Step 2: Python does the comparison (exact, no guessing)
        def matches(skill):
            s = skill.lower()
            return any(s in m or m in s for m in my_lower)

        have = [s for s in job_skills if matches(s)]
        missing = [s for s in job_skills if not matches(s)]

print("Skills required:", ", ".join(job_skills))
print("You HAVE:       ", ", ".join(have) or "None")
print("You are MISSING:", ", ".join(missing) or "None")
print(f"Match score:     {score}/100")