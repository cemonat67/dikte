from openai import OpenAI

client = OpenAI()

def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = load_prompt("prompts/ai_system.txt")
ANOMALY_PROMPT = load_prompt("prompts/anomaly_strict.txt")


def ask_ai(user_input, mode="normal"):
    if mode == "anomaly":
        system = SYSTEM_PROMPT + "\n\n" + ANOMALY_PROMPT
    else:
        system = SYSTEM_PROMPT

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # ucuz + yeterli
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_input}
        ],
        temperature=0.2,   # düşük = daha deterministic
        max_tokens=120     # kontrol
    )

    return response.choices[0].message.content
