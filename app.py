import json
import ollama
import streamlit as st

client = ollama.Client(timeout=120)  # stop after 2 minutes

st.title("JD Skill Matcher")
st.write("Paste a job description and see how well your skills match.")

try:
    with open("my_skills.txt", "r", encoding="utf-8") as f:
        default_skills = f.read()
except FileNotFoundError:
    default_skills = ""

jd = st.text_area("Job description", height=250)
skills_text = st.text_area("Your skills (one per line)", value=default_skills, height=200)


def matches(skill, my_lower):
    """True if the skills are the same, or one is the other plus extra words.
    'Backend' matches 'Backend development', but 'Java' does not match 'JavaScript'."""
    s = skill.lower().strip()
    for m in my_lower:
        if s == m or m.startswith(s + " ") or s.startswith(m + " "):
            return True
    return False


if st.button("Check match"):
    if not jd.strip():
        st.warning("Please paste a job description first.")
    else:
        short_jd = jd[:3000]  # use the first 3000 characters only
        try:
            with st.spinner("Reading job description..."):
                response = client.chat(
                    model="llama3.2",
                    messages=[{
                        "role": "user",
                        "content": f"""List only the specific technologies, programming languages, frameworks, tools and technical skills required in this job description.
Do NOT include company product names, business areas, team names or vague phrases.
Include AI/ML skills such as LLMs, RAG, machine learning and cloud services, and include API and backend skills.
Return ONLY JSON in this format: {{"skills": ["skill1", "skill2"]}}

Job description:
{short_jd}"""
                    }],
                    format="json",
                    options={"temperature": 0, "num_predict": 300},
                )
                job_skills = json.loads(response["message"]["content"])["skills"]
        except Exception as e:
            st.error(f"Something went wrong: {e}. Try again or use a shorter job description.")
            st.stop()

        my_skills = [s.strip().rstrip(",") for s in skills_text.splitlines() if s.strip()]
        my_lower = [s.lower() for s in my_skills]
        have = [s for s in job_skills if matches(s, my_lower)]
        missing = [s for s in job_skills if not matches(s, my_lower)]
        score = round(len(have) / len(job_skills) * 100) if job_skills else 0

        st.metric("Match score", f"{score}/100")
        st.progress(score / 100)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ You have")
            for s in have or ["None"]:
                st.write("-", s)
        with col2:
            st.subheader("❌ Missing")
            for s in missing or ["None"]:
                st.write("-", s)