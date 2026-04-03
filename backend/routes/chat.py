from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.llm import chat_completion, extract_traits_from_conversation
from services.memory import (
    build_system_prompt,
    add_message,
    get_recent_messages,
    add_trait,
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with a persona. Sends user message, gets LLM response, extracts traits."""

    persona_id = req.persona_id
    user_message = req.message

    # 1. Store the user message
    add_message(persona_id, "user", user_message)

    # 2. Build the dynamic system prompt (Layer 1 + Layer 2)
    system_prompt = build_system_prompt(persona_id)

    # 3. Get recent conversation history for context
    history = get_recent_messages(persona_id, limit=20)

    # 4. Get LLM response from Groq
    reply_text = chat_completion(system_prompt, history)

    # 5. Store the assistant's reply
    add_message(persona_id, "assistant", reply_text)

    # 6. Extract any new character traits from this exchange
    new_traits = extract_traits_from_conversation(user_message, reply_text)
    stored_traits = []
    for trait in new_traits:
        trait_id = add_trait(persona_id, trait, learned_from=f"chat: {user_message[:50]}")
        if trait_id > 0:  # Only count non-duplicate traits
            stored_traits.append(trait)

    if stored_traits:
        print(f"🧠 Learned {len(stored_traits)} new traits: {stored_traits}")

    return ChatResponse(reply=reply_text, new_traits_learned=stored_traits)
