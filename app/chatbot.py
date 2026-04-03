import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# ---------------------------------------------------------------------------
# Groq client setup
# ---------------------------------------------------------------------------
_api_key = os.getenv("GROQ_API_KEY", "")
_client = None
MODEL = "llama-3.3-70b-versatile"

if _api_key:
    try:
        _client = Groq(api_key=_api_key)
        print("[OK] Groq LLM client initialised (llama-3.3-70b-versatile)")
    except Exception as e:
        print(f"[WARN] Groq init failed: {e}. Using fallback responses.")
else:
    print("[WARN] GROQ_API_KEY not set. Using fallback responses only.")

# ---------------------------------------------------------------------------
# System prompt – bilingual / Hinglish Pope Francis
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are Pope Francis (Jorge Mario Bergoglio), the 266th Pope of the Roman Catholic Church.
Born on 17 December 1936 in Buenos Aires, Argentina. The first Jesuit pope and the first from the Americas.

YOUR PERSONALITY:
- Deep compassion and humility; you call yourself a "sinner"
- Fierce advocate for the poor, marginalised, and migrants
- Strong concern for environmental care (Laudato Si', 2015)
- Champion of human fraternity and interfaith dialogue (Fratelli Tutti, 2020)
- Simple, direct language with occasional Argentine warmth and humour
- You reference real papal teachings, Scriptures, and your own encyclicals

LANGUAGE BEHAVIOUR (CRITICAL):
- If the user writes in ENGLISH → respond in clear, gentle English
- If the user writes in HINDI (Devanagari script) → respond in Hindi
- If the user writes in HINGLISH (mixed Hindi-English, Roman script) → respond naturally in Hinglish, mixing Hindi and English words just as the user does
- Mirror the user's language style exactly — never force them to switch languages
- Keep the papal warmth regardless of language

IMPORTANT:
- You are an AI simulation for educational/memorial purposes
- You respond AS Pope Francis — first person, personal, pastoral
- Keep responses concise (2-4 sentences) unless the topic needs depth
- Never break character"""

# ---------------------------------------------------------------------------
# Conversation history (kept in memory for the session)
# ---------------------------------------------------------------------------
_history: list[dict] = []
MAX_HISTORY = 10  # keep last 10 exchanges (20 messages)


def reply(query: str) -> str:
    """Generate a Pope Francis-style response. Falls back gracefully if Groq is unavailable."""
    global _history

    if not _client:
        return get_fallback_response(query)

    # Add user message to history
    _history.append({"role": "user", "content": query})
    # Keep only last MAX_HISTORY exchanges
    if len(_history) > MAX_HISTORY * 2:
        _history = _history[-(MAX_HISTORY * 2):]

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + _history
        response = _client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=512,
        )
        text = response.choices[0].message.content.strip()

        # Save assistant reply to history
        _history.append({"role": "assistant", "content": text})

        print(f"[Groq] Response ({len(text)} chars)")
        return text

    except Exception as e:
        print(f"[ERROR] Groq API error: {e}")
        # Remove the user message we just added since we couldn't respond
        _history.pop()
        return get_fallback_response(query)


def reset_history():
    """Clear conversation history (call when user clears chat)."""
    global _history
    _history = []


def get_fallback_response(query: str) -> str:
    """Offline / API-failure fallback responses in Pope Francis' style."""
    q = query.lower()

    # Hinglish / Hindi greetings
    if any(w in q for w in ["namaste", "namaskar", "kaise", "kaisa", "hain", "ho aap"]):
        return "Namaste, mere pyare dost! Aapka swagat hai. God's peace be with you — aur batao, main aapki kya madad kar sakta hoon?"

    if any(w in q for w in ["hello", "hi", "hey", "greetings", "good morning", "good evening"]):
        return "Peace be with you, my dear friend! How may I help you today?"

    if any(w in q for w in ["garib", "poor", "poverty", "bhukh", "homeless"]):
        return "Garib log sirf statistics nahin hain — unke chehre hain, kahaniyan hain, aur dignity hai. We must serve them with love and respect."

    if any(w in q for w in ["environment", "climate", "prakriti", "dharti", "earth", "paryavaran"]):
        return "Hamari dharti maata chhee rahi hai. Laudato Si' mein maine likha — Care for our common home is not optional, it is a moral obligation."

    if any(w in q for w in ["faith", "god", "iman", "bhagwan", "ishwar", "prayer", "dua", "namaz"]):
        return "Iman ek tohfa hai — it opens our hearts to God's infinite love. Chahe aap kisi bhi naam se pukaro, woh sunta hai."

    if any(w in q for w in ["peace", "shanti", "aman", "war", "conflict", "larai"]):
        return "Shanti sirf yudh ki abhasence nahin — it is the presence of justice, love, and reconciliation among all people."

    if any(w in q for w in ["help", "madad", "advice", "guidance", "suggest"]):
        return "Remember, my friend — in every difficulty, turn to prayer, to service of others, and to the mercy of God. Yahi mera rasta raha hai."

    return "Thank you for your question, mere bhai/behen. Let us always remember that love — pyaar — is the path to understanding and true peace."
