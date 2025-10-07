import requests
import json
from typing import List, Tuple, Optional
import time

# Performance cache for common queries
_response_cache = {}
_cache_timeout = 300  # 5 minutes

# Common question patterns with fast responses
QUICK_RESPONSES = {
    "python programming": "Python is a popular, easy-to-learn programming language known for its simple syntax and powerful libraries. It's great for beginners and used in web development, data science, AI, and automation.",
    "computers work": "Computers work by processing data through the CPU, storing information in memory and storage, and using input/output devices. The operating system manages resources while applications provide specific functionality.",
    "artificial intelligence": "AI is technology that enables machines to perform tasks requiring human-like intelligence, such as learning, reasoning, and pattern recognition. It uses algorithms and data to make decisions.",
    "machine learning": "Machine Learning is a subset of AI where computers learn patterns from data without explicit programming. It's used in recommendations, predictions, and automated decision-making.",
    "who made you": "I was created by Abhiram. I'm an offline AI assistant built with Python and local libraries to run without the internet.",
    "how were you made": "I was created by Abhiram using Python, Ollama for local AI, MySQL for data storage, and various system control libraries for comprehensive laptop management."
}

def get_quick_response(prompt: str) -> Optional[str]:
    """Check if we have a quick response for common queries"""
    prompt_lower = prompt.lower()
    for pattern, response in QUICK_RESPONSES.items():
        if pattern in prompt_lower:
            return response
    return None

def _format_history(history: List[Tuple[str, str, str]], max_chars: int = 1500) -> str:
    """Format last conversation rows - reduced size for faster processing"""
    if not history:
        return ""
    parts = []
    # Only use last 3 conversations for speed
    for user, assistant, _ts in reversed(history[-3:]):
        if user:
            parts.append(f"User: {user}")
        if assistant:
            parts.append(f"Assistant: {assistant}")
    text = "\n".join(parts)
    if len(text) > max_chars:
        text = text[-max_chars:]
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl+1:]
    return text


def ask_ai(prompt: str, *, history: Optional[List[Tuple[str, str, str]]] = None,
           system: Optional[str] = None, model: str = "phi3:latest", timeout: int = 8) -> str:
    """Call local LLM with optimizations for speed"""
    
    # Check for quick responses first
    quick_response = get_quick_response(prompt)
    if quick_response:
        return f"Hello Abhi Ram! {quick_response}"
    
    # Check cache
    cache_key = f"{prompt[:100]}_{model}"
    current_time = time.time()
    
    if cache_key in _response_cache:
        cached_response, cached_time = _response_cache[cache_key]
        if current_time - cached_time < _cache_timeout:
            return f"{cached_response} (cached)"
    
    try:
        # Simplified context for faster processing
        context = _format_history(history or [])
        
        # Shorter system message for faster processing
        sys_text = system or "You are Abhi Ram's offline assistant. Be concise and helpful."
        
        # Simplified prompt structure
        if context:
            composite_prompt = f"{sys_text}\n\nContext: {context}\n\nUser: {prompt}\n\nAssistant:"
        else:
            composite_prompt = f"{sys_text}\n\nUser: {prompt}\n\nAssistant:"
        
        # Reduced timeout for faster responses
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model, 
                "prompt": composite_prompt,
                "options": {
                    "num_predict": 150,  # Limit response length for speed
                    "temperature": 0.7,   # Reduce randomness for faster generation
                    "top_k": 20,         # Reduce choices for speed
                    "top_p": 0.9         # Focus on likely tokens
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
        
        # Cache the response
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