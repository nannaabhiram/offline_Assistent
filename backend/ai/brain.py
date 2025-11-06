import requests
import json
from typing import List, Tuple, Optional
import time

# Import RAG functionality
try:
    from ai.rag import enhance_with_rag, get_rag_status
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG module not available")

# Performance cache for common queries
_response_cache = {}
_cache_timeout = 60  # 5 minutes

# Common question patterns with fast responses
QUICK_RESPONSES = {
    "python programming": "Python is a popular programming language - simple syntax, powerful libraries, great for beginners and experts alike.",
    "computers work": "Computers process data through the CPU, store info in memory/storage, and use input/output devices. The OS manages everything while apps provide specific functions.",
    "artificial intelligence": "AI enables machines to perform human-like tasks using algorithms and data to learn, reason, and make decisions.",
    "machine learning": "Machine Learning is AI where computers learn patterns from data without explicit programming - used for recommendations and predictions.",
    "who made you": "I was created by Abhiram using Python and local AI models.",
    "how were you made": "Built with Python, Ollama for local AI, MySQL for data, and system control libraries for laptop management.",
    "how to make pasta": "To make pasta: 1) Boil 4-6 quarts of salted water. 2) Add pasta and stir occasionally. 3) Cook 8-12 minutes until al dente. 4) Drain and serve with your favorite sauce!",
    "cook pasta": "Boil salted water, add pasta, cook 8-12 minutes stirring occasionally, drain when al dente (firm to bite), then add sauce.",
}

def get_quick_response(prompt: str) -> Optional[str]:
    """Check if we have a quick response for common queries"""
    prompt_lower = prompt.lower()
    for pattern, response in QUICK_RESPONSES.items():
        if pattern in prompt_lower:
            return response
    return None

def _format_history(history: List[Tuple[str, str, str]], max_chars: int = 2500) -> str:
    """Format last conversation rows - includes more context for better continuity"""
    if not history:
        return ""
    parts = []
    # Use last 5-8 conversations for better context (increased from 3)
    recent_history = history[-8:] if len(history) > 8 else history
    
    for user, assistant, _ts in recent_history:
        if user:
            parts.append(f"User: {user}")
        if assistant:
            # Remove "(cached)" suffix if present
            clean_assistant = assistant.replace(" (cached)", "")
            parts.append(f"Assistant: {clean_assistant}")
    
    text = "\n".join(parts)
    
    # Truncate if too long, but keep complete conversations
    if len(text) > max_chars:
        text = text[-max_chars:]
        # Find first complete user message
        first_nl = text.find("\nUser: ")
        if first_nl != -1:
            text = text[first_nl+1:]
    
    return text


def ask_ai(prompt: str, *, history: Optional[List[Tuple[str, str, str]]] = None,
           system: Optional[str] = None, model: str = "llama3.2:1b", timeout: int = 12,
           use_rag: bool = True) -> str:
    """Call local LLM with optimizations for speed and optional RAG enhancement"""
    
    # Check for quick responses first
    quick_response = get_quick_response(prompt)
    if quick_response:
        return quick_response
    
    # Apply RAG if available and enabled
    rag_used = False
    if use_rag and RAG_AVAILABLE:
        try:
            enhanced_prompt, rag_used = enhance_with_rag(prompt)
            if rag_used:
                prompt = enhanced_prompt
                print("🌐 RAG: Using real-time internet information")
        except Exception as e:
            print(f"⚠️ RAG error (continuing without): {e}")
    
    # Check cache (skip cache if RAG was used for real-time info)
    if not rag_used:
        cache_key = f"{prompt[:100]}_{model}"
        current_time = time.time()
        
        if cache_key in _response_cache:
            cached_response, cached_time = _response_cache[cache_key]
            if current_time - cached_time < _cache_timeout:
                return f"{cached_response} (cached)"
    
    try:
        # Get conversation history for context
        context = _format_history(history or [])
        
        # Better system message - more direct and informative, emphasizes using conversation history
        if system:
            sys_text = system
        else:
            sys_text = "You are a helpful AI assistant. Give direct, informative answers. Don't ask follow-up questions unless necessary. Be concise but complete. Use the conversation history to maintain context and remember what was discussed."
        
        # Build prompt with context
        if context:
            composite_prompt = f"{sys_text}\n\nRecent Conversation:\n{context}\n\nUser: {prompt}\n\nAssistant:"
        else:
            composite_prompt = f"{sys_text}\n\nUser: {prompt}\n\nAssistant:"
        
        # Adjust token count based on whether RAG is used
        num_tokens = 150 if rag_used else 80  # Increased from 40 to 80 for better answers
        
        # Reduced timeout for faster responses
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model, 
                "prompt": composite_prompt,
                "options": {
                    "num_predict": num_tokens,  # More tokens when RAG is used
                    "temperature": 0.3 if rag_used else 0.2,  # Slightly higher for better answers
                    "top_k": 30 if rag_used else 20,  # More choices
                    "top_p": 0.9 if rag_used else 0.85,  # More diverse
                    "repeat_penalty": 1.1  # Prevent repetition
                }
            },
            stream=True,
            timeout=timeout,
        )
        
        result = ""
        start_time = time.time()
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                result += data.get("response", "")
                
                # Stop if taking too long
                if time.time() - start_time > timeout:
                    result += " [Response truncated for speed]"
                    break
        
        final_response = result.strip()
        
        # Cache the response (only if RAG wasn't used)
        if not rag_used:
            _response_cache[cache_key] = (final_response, current_time)
            
            # Keep cache size manageable
            if len(_response_cache) > 50:
                # Remove oldest entries
                oldest_key = min(_response_cache.keys(), key=lambda k: _response_cache[k][1])
                del _response_cache[oldest_key]
        
        return final_response
        
    except requests.exceptions.Timeout:
        return "AI response timeout - the model is taking too long to respond. Try a simpler question."
    except requests.exceptions.RequestException as e:
        return f"AI Error: {e}"