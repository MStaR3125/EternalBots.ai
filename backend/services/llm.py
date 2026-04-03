import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def chat_completion(system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
    """Send a chat completion request to Groq."""
    try:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = client.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            temperature=temperature,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return "I'm having trouble thinking right now. Could you try again?"


def extract_facts_from_text(text: str) -> list[str]:
    """Use the LLM to extract factual information from uploaded text."""
    system = (
        "You are a fact extractor. Given a text about a person, extract every distinct factual statement. "
        "Return ONLY a JSON array of strings, each being one fact. Example: "
        '[\"Born on March 5, 1940\", \"Worked as a carpenter\", \"Lived in Mumbai\"]. '
        "Be thorough. Extract names, dates, places, relationships, occupations, events, achievements."
    )
    messages = [{"role": "user", "content": f"Extract all facts from this text:\n\n{text}"}]

    try:
        result = chat_completion(system, messages, temperature=0.2)
        # Parse JSON array from response
        import json
        # Clean up response - find the JSON array
        start = result.find("[")
        end = result.rfind("]") + 1
        if start != -1 and end > start:
            facts = json.loads(result[start:end])
            return [f for f in facts if isinstance(f, str) and len(f.strip()) > 3]
        return []
    except Exception as e:
        print(f"❌ Fact extraction error: {e}")
        return []


def extract_traits_from_conversation(user_message: str, assistant_reply: str) -> list[str]:
    """After a conversation exchange, extract any new personality traits mentioned by the user."""
    system = (
        "You analyze conversations to extract personality traits, preferences, habits, and mannerisms "
        "that the USER reveals about the person they are talking to (the AI avatar). "
        "Return ONLY a JSON array of trait strings. If no new traits are mentioned, return []. "
        "Focus on: personality quirks, habits, preferences, catchphrases, emotional patterns, "
        "relationships, hobbies, opinions. Do NOT extract facts (dates, places, names) — only character traits."
    )
    messages = [
        {
            "role": "user",
            "content": (
                f"User said to the avatar: \"{user_message}\"\n"
                f"Avatar replied: \"{assistant_reply}\"\n\n"
                "What personality traits or character details did the user reveal about the person?"
            ),
        }
    ]

    try:
        result = chat_completion(system, messages, temperature=0.3)
        import json
        start = result.find("[")
        end = result.rfind("]") + 1
        if start != -1 and end > start:
            traits = json.loads(result[start:end])
            return [t for t in traits if isinstance(t, str) and len(t.strip()) > 3]
        return []
    except Exception as e:
        print(f"❌ Trait extraction error: {e}")
        return []
