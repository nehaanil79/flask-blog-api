import json

from flask import current_app
from groq import Groq

MODEL = "openai/gpt-oss-20b"
MAX_TAGS = 5

SYSTEM_PROMPT = (
    "You suggest tags for blog posts. "
    "Reply with JSON only, in this exact shape: "
    '{"tags": ["tag one", "tag two"]}. '
    "Give 3 to 5 short tags (1 to 3 words each), lowercase, "
    "about the main topics of the post. No hashtags."
)


class AIServiceError(Exception):
    """Raised when the AI service fails or returns something unusable."""


def clean_tags(raw_tags):
    if not isinstance(raw_tags, list):
        return []

    tags = []
    for tag in raw_tags:
        if not isinstance(tag, str):
            continue
        tag = tag.strip().lower().lstrip("#")
        if tag and len(tag) <= 30 and tag not in tags:
            tags.append(tag)

    return tags[:MAX_TAGS]


def suggest_tags(title, content):
    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        raise AIServiceError("AI service is not configured.")

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Title: {title}\n\nContent: {content[:4000]}"},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            reasoning_effort="low",
        )
        data = json.loads(response.choices[0].message.content)
    except Exception as error:
        raise AIServiceError("AI service is unavailable. Please try again later.") from error

    tags = clean_tags(data.get("tags"))
    if not tags:
        raise AIServiceError("AI service returned no usable tags.")

    return tags