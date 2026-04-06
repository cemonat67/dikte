from pathlib import Path
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"

client = OpenAI()


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


SYSTEM_PROMPT = load_prompt("ai_system.txt")
ANOMALY_PROMPT = load_prompt("anomaly_strict.txt")


def ask_ai(user_input: str, mode: str = "normal", model: str = "gpt-4.1-mini") -> str:
    system = SYSTEM_PROMPT
    if mode == "anomaly":
        system = f"{SYSTEM_PROMPT}\n\n{ANOMALY_PROMPT}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_input.strip()},
        ],
        temperature=0.2,
        max_tokens=120,
    )

    return (response.choices[0].message.content or "").strip()
