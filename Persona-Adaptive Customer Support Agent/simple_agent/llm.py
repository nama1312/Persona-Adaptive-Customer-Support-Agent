import os
from openai import OpenAI

def generate_llm_reply(persona, message, kb_snippets):
    """
    set OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "LLM unavailable (missing OPENAI_API_KEY)."

    client = OpenAI(api_key=api_key)

    kb_text = "\n".join([f"- {k['title']}: {k['content']}" for k in kb_snippets]) \
              if kb_snippets else "No matching KB article found."

    system_prompt = (
        "You are a simple support agent. "
        "Write short, clear responses. "
        "Adapt tone based on persona."
    )

    user_prompt = f"""
Persona: {persona}
User message: {message}

Relevant KB:
{kb_text}

Write a short helpful reply:
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=200,
        temperature=0.4
    )

    return completion.choices[0].message.content.strip()
