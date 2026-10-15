import os
import json
from dotenv import load_dotenv
from groq import Groq
from google import genai
from pydantic import BaseModel

load_dotenv()


class LLMAdapter:
    def __init__(self, generate_response):
        self.generate_response = generate_response

    def __call__(self, prompt: str) -> str:
        return self.generate_response(prompt)

    def invoke(self, prompt: str) -> str:
        return self.generate_response(prompt)

    def with_structured_output(self, schema: type[BaseModel]):
        class StructuredOutputAdapter:
            def invoke(self, prompt: str) -> BaseModel:
                structured_prompt = (
                    f"{prompt}\n\n"
                    "Return only a JSON object matching this JSON schema. "
                    "Do not include markdown fences or additional text.\n"
                    f"{json.dumps(schema.model_json_schema())}"
                )
                response = self_generate_response(structured_prompt)
                return schema.model_validate_json(response.strip())

        self_generate_response = self.generate_response
        return StructuredOutputAdapter()


def pick_llm(level: str | None = None):
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

    return LLMAdapter(generate_response)


if __name__ == "__main__":
    generate_response = pick_llm()

    answer = generate_response(
        "Explain RAG in simple terms."
    )
    print(answer)
