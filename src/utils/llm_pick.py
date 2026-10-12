import os
from dotenv import load_dotenv
from groq import Groq
from google import genai

load_dotenv()


def pick_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

        def generate_response(prompt: str) -> str:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content or ""

    elif provider == "gemini":
        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        def generate_response(prompt: str) -> str:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text or ""

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )

    return generate_response


if __name__ == "__main__":
    generate_response = pick_llm()

    answer = generate_response(
        "Explain RAG in simple terms."
    )
    print(answer)
