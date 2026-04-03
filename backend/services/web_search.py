from duckduckgo_search import DDGS
from services.llm import chat_completion
from db.database import get_db

def perform_web_search_for_facts(persona_id: int):
    """
    Looks up the persona name in DuckDuckGo, extracts facts using the LLM,
    and adds them to the database.
    """
    conn = get_db()
    persona = conn.execute("SELECT name, description FROM personas WHERE id = ?", (persona_id,)).fetchone()
    if not persona:
        conn.close()
        return

    name = persona["name"]
    desc = persona["description"] or ""
    conn.close()

    try:
        print(f"🔍 Searching web for: {name} {desc}")
        query = f"{name} {desc} biography facts"
        
        # Search DDG
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        if not results:
            print("⚠️ No web search results found.")
            return
            
        # Combine snippets
        context_text = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        print(f"📄 Found web context for {name}, extracting facts...")
        
        # Use LLM to extract facts from search results
        system = (
            "You are a fact extractor. Given web search results about a person, extract distinct factual statements. "
            "Return ONLY a JSON array of strings, each being one fact. Example: "
            '[\"Born on March 5, 1940\", \"Is the head of the Catholic Church\"]. '
            "Be thorough and focus on permanent or historical facts."
        )
        messages = [{"role": "user", "content": f"Extract facts about {name} from these web results:\n\n{context_text}"}]
        
        result = chat_completion(system, messages, temperature=0.2)
        
        import json
        start = result.find("[")
        end = result.rfind("]") + 1
        if start != -1 and end > start:
            facts = json.loads(result[start:end])
            
            # Save to database
            from services.memory import add_fact
            count = 0
            for fact in facts:
                if isinstance(fact, str) and len(fact.strip()) > 3:
                    add_fact(persona_id, fact.strip(), source="web_search")
                    count += 1
            print(f"✅ Added {count} facts from web search for {name}.")
            
    except Exception as e:
        print(f"❌ Web search error: {e}")
