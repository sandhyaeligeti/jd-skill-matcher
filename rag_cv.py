import math
import ollama

client = ollama.Client(timeout=120)

# 1. Load the CV and split it into small chunks (5 lines each)
with open("cv.txt", "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

chunks = ["\n".join(lines[i:i + 5]) for i in range(0, len(lines), 5)]
print(f"Loaded CV: {len(chunks)} chunks")


# 2. Turn text into embeddings (numbers that capture meaning)
def embed(texts):
    return client.embed(model="nomic-embed-text", input=texts)["embeddings"]


def similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


print("Creating embeddings...")
chunk_vectors = embed(chunks)
print("Ready!\n")

# 3. Ask questions in a loop
while True:
    question = input("Ask about your CV (or type exit): ")
    if question.lower() == "exit":
        break

    # Retrieval: find the 3 chunks most similar in meaning to the question
    q_vector = embed([question])[0]
    scored = sorted(
        zip(chunks, chunk_vectors),
        key=lambda pair: similarity(q_vector, pair[1]),
        reverse=True,
    )
    top_chunks = [chunk for chunk, _ in scored[:3]]
    context = "\n\n".join(top_chunks)

    # Generation: answer using ONLY those chunks
    response = client.chat(
        model="llama3.2",
        messages=[{
            "role": "user",
            "content": f"""Answer the question using ONLY the CV text below.
If the answer is not in the CV text, say "Not mentioned in the CV."

CV text:
{context}

Question: {question}"""
        }],
        options={"temperature": 0, "num_predict": 300},
    )
    print("\nAnswer:", response["message"]["content"])
    print("\n--- Based on these parts of your CV ---")
    print(context)
    print("---------------------------------------\n")