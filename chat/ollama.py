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
    from chat.models import UserMessage

    messages = []

    messages.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })

    # take recent user messages and their assistant replies
    qs = UserMessage.objects.filter(
        conversation=conversation).order_by('-created_at')[:12]
    for um in reversed(qs):
        messages.append({"role": "user", "content": um.content})
        assistant = getattr(um, 'assistant_reply', None)
        if assistant:
            messages.append(
                {"role": "assistant", "content": assistant.content})

    return messages


def generate_title_from_conversation(assistant_reply):
    try:
        message = f"""Provide a very short title (one line, max 60 characters).
                that summarizes the conversation. Reply with the title only.
                Conversation summary: {assistant_reply}"""

        title = chat_with_ollama([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ])
        if not title:
            raise ValueError("empty title from model")
        return title.strip()[:60]
    except Exception as e:
        return None
