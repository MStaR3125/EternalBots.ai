from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

# Load model and tokenizer with better error handling
print("Loading TinyLlama chatbot model...")
try:
    tok = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    # Set pad_token to eos_token to fix attention mask warning
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype=torch.float16, device_map="auto")
    print("✅ TinyLlama model loaded successfully!")
    MODEL_LOADED = True
except Exception as e:
    print(f"⚠️ Could not load TinyLlama model: {e}")
    print("Using fallback responses only (no AI generation)")
    tok = None
    model = None
    MODEL_LOADED = False

def reply(query: str) -> str:
    """Generate a Pope Francis-style response to the query"""
    
    # If model not loaded, use fallback immediately
    if not MODEL_LOADED or model is None or tok is None:
        print("Using fallback response (model not available)")
        return get_fallback_response(query)
    
    # Enhanced prompt with more specific instructions
    prompt = f"""You are Pope Francis, the Pope of the Catholic Church. You speak with:
- Deep compassion and humility
- Care for the poor and marginalized  
- Concern for environmental issues
- Simple, accessible language
- Wisdom and gentleness
- References to faith, love, and mercy

Question: {query}
Pope Francis responds:"""

    try:
        # Generate response with adjusted parameters
        inputs = tok(prompt, return_tensors="pt", max_length=512, truncation=True, 
                    padding=True)  # Added padding=True
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids.to(model.device),
                attention_mask=inputs.attention_mask.to(model.device),  # Added attention_mask
                max_new_tokens=100,
                temperature=0.8,
                do_sample=True,
                pad_token_id=tok.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode and clean the response
        full_response = tok.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the Pope's response
        if "Pope Francis responds:" in full_response:
            response = full_response.split("Pope Francis responds:")[-1].strip()
        elif "responds:" in full_response:
            response = full_response.split("responds:")[-1].strip()
        else:
            response = full_response.split(query)[-1].strip()
        
        # Clean up the response
        response = clean_response(response)
        
        # Fallback to ensure a proper papal response
        if len(response) < 10 or not response:
            response = get_fallback_response(query)
            
        return response
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return get_fallback_response(query)

def clean_response(response: str) -> str:
    """Clean and format the response"""
    # Remove common artifacts
    response = re.sub(r'^[^\w]*', '', response)  # Remove leading non-word chars
    response = re.sub(r'\n+', ' ', response)  # Replace newlines with spaces
    response = re.sub(r'\s+', ' ', response)  # Normalize whitespace
    
    # Ensure proper ending
    if response and not response.endswith(('.', '!', '?')):
        response += '.'
    
    # Capitalize first letter
    if response:
        response = response[0].upper() + response[1:]
    
    return response.strip()

def get_fallback_response(query: str) -> str:
    """Provide appropriate fallback responses in Pope Francis' style"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['hello', 'hi', 'greetings']):
        return "Peace be with you, my dear friend. How may I help you today?"
    
    elif any(word in query_lower for word in ['help', 'advice', 'guidance']):
        return "Remember that God's love is always with you. In times of difficulty, turn to prayer and acts of compassion for others."
    
    elif any(word in query_lower for word in ['poor', 'poverty', 'homeless']):
        return "The poor are not statistics, they are people with faces, stories, and dignity. We must always remember to serve them with love and respect."
    
    elif any(word in query_lower for word in ['environment', 'earth', 'climate']):
        return "Our common home, the Earth, cries out to us. We must care for creation as God entrusted it to us, for future generations."
    
    elif any(word in query_lower for word in ['faith', 'god', 'jesus', 'prayer']):
        return "Faith is a gift that opens our hearts to God's infinite love. Through prayer, we find peace and strength for our journey."
    
    elif any(word in query_lower for word in ['peace', 'war', 'conflict']):
        return "Peace is not merely the absence of war, but the presence of justice, love, and reconciliation among all people."
    
    else:
        return "Thank you for your question. Let us always remember that love and compassion are the paths to understanding and peace."
