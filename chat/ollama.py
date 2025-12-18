import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3"

SYSTEM_PROMPT = """
You are a helpful, accurate, and concise AI chat assistant.
Maintain conversational context.
Ask clarifying questions when needed.
"""


def chat_with_ollama(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    return response.json()["message"]["content"]


def build_context(conversation):
    messages = []

    messages.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })

    qs = conversation.messages.order_by('-created_at')[:12]
    for msg in reversed(qs):
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    return messages
