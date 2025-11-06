"""
RAG (Retrieval-Augmented Generation) Module
Enhances AI responses with real-time internet information using SerpAPI
"""
import os
import requests
import subprocess
import time
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()


def check_wifi_status() -> Dict:
    """Check if WiFi is connected"""
    try:
        # Try to ping Google to check internet connectivity
        response = requests.get("http://www.google.com", timeout=3)
        return {
            'connected': True,
            'status': 'Connected',
            'can_connect': True
        }
    except requests.exceptions.RequestException:
        # WiFi might be off or no internet
        return {
            'connected': False,
            'status': 'Disconnected',
            'can_connect': True
        }


def get_wifi_interface_name() -> Optional[str]:
    """Get the WiFi interface name on Windows"""
    try:
        # List all network interfaces
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            # Look for wireless/WiFi interfaces
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['wi-fi', 'wireless', 'wlan']):
                    # Extract interface name (usually the last column)
                    parts = line.split()
                    if len(parts) >= 4:
                        # Get the interface name (last part)
                        return ' '.join(parts[3:]).strip()
        
        # Common interface names to try
        common_names = ['Wi-Fi', 'WiFi', 'Wireless', 'WLAN', 'Wireless Network Connection']
        return common_names[0]  # Default to Wi-Fi
        
    except Exception as e:
        print(f"Error getting WiFi interface: {e}")
        return 'Wi-Fi'  # Default fallback


def enable_wifi() -> Dict:
    """Enable WiFi adapter on Windows"""
    try:
        # Get the correct WiFi interface name
        wifi_interface = get_wifi_interface_name()
        print(f"📡 Attempting to enable WiFi interface: {wifi_interface}")
        
        # Try multiple methods to enable WiFi
        
        # Method 1: Using netsh interface set
        result1 = subprocess.run(
            ['netsh', 'interface', 'set', 'interface', wifi_interface, 'enabled'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Method 2: Using netsh wlan if Method 1 fails
        if result1.returncode != 0:
            print("📡 Trying alternative method...")
            result2 = subprocess.run(
                ['netsh', 'wlan', 'connect', 'name=*'],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        # Wait a moment for WiFi to initialize
        print("⏳ Waiting for WiFi adapter to initialize...")
        time.sleep(5)
        
        # Try to reconnect to a known network
        try:
            # This will attempt to connect to any available saved network
            subprocess.run(
                ['netsh', 'wlan', 'connect', 'ssid=*', 'name=*'],
                capture_output=True,
                text=True,
                timeout=5
            )
            time.sleep(3)
        except:
            pass
        
        # Check if connected
        wifi_status = check_wifi_status()
        
        if wifi_status['connected']:
            return {
                'success': True,
                'message': 'WiFi enabled and connected successfully',
                'connected': True
            }
        else:
            return {
                'success': True,
                'message': 'WiFi adapter enabled but not yet connected to a network',
                'connected': False
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': 'WiFi enable command timed out',
            'connected': False
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error enabling WiFi: {str(e)}',
            'connected': False
        }


def smart_wifi_connect() -> Dict:
    """
    Smart WiFi connection: Check status, enable if needed, verify connection
    """
    # Step 1: Check current WiFi status
    wifi_status = check_wifi_status()
    
    if wifi_status['connected']:
        return {
            'success': True,
            'message': 'WiFi is already connected',
            'already_connected': True,
            'actions_taken': []
        }
    
    # Step 2: WiFi is not connected, try to enable it
    actions = []
    actions.append('Checking WiFi adapter...')
    
    enable_result = enable_wifi()
    actions.append(f'Attempted to enable WiFi: {enable_result["message"]}')
    
    if enable_result['success'] and enable_result['connected']:
        return {
            'success': True,
            'message': 'WiFi connected successfully',
            'already_connected': False,
            'actions_taken': actions
        }
    elif enable_result['success'] and not enable_result['connected']:
        return {
            'success': False,
            'message': 'WiFi adapter enabled but no network available. Please check if you have WiFi networks in range or verify network credentials.',
            'reason': 'No available networks or incorrect credentials',
            'already_connected': False,
            'actions_taken': actions
        }
    else:
        return {
            'success': False,
            'message': 'Could not enable WiFi adapter. Please check if WiFi hardware is available.',
            'reason': enable_result['message'],
            'already_connected': False,
            'actions_taken': actions
        }


def activate_online_mode_with_wifi() -> Dict:
    """
    Smart online mode activation with automatic WiFi connection
    """
    # Step 1: Try to connect WiFi
    wifi_result = smart_wifi_connect()
    
    if not wifi_result['success']:
        return {
            'success': False,
            'message': f"Cannot activate online mode: {wifi_result['message']}",
            'wifi_status': wifi_result,
            'online_mode_active': False
        }
    
    # Step 2: WiFi is connected, check if SerpAPI key is configured
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key:
        return {
            'success': False,
            'message': 'WiFi connected but SerpAPI key is not configured.',
            'wifi_status': wifi_result,
            'online_mode_active': False
        }
    
    # Step 3: Activate online mode
    global online_mode_active
    online_mode_active = True
    
    wifi_msg = "WiFi was already connected" if wifi_result.get('already_connected') else "WiFi connected successfully"
    
    return {
        'success': True,
        'message': f"{wifi_msg}. Online mode activated! I can now search the internet for real-time information.",
        'wifi_status': wifi_result,
        'online_mode_active': True
    }

def should_use_rag(query: str) -> bool:
    """
    Determine if a query needs real-time information from the internet.
    Returns True for queries about current events, news, weather, etc.
    """
    # Keywords that indicate need for real-time information
    realtime_keywords = [
        'weather', 'news', 'latest', 'current', 'today', 'now', 'recent',
        'update', 'price', 'stock', 'score', 'result', 'happening',
        'this week', 'this month', 'this year', '2024', '2025',
        'forecast', 'live', 'breaking', 'trending'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in realtime_keywords)


def search_serp(query: str, num_results: int = 3) -> Optional[Dict]:
    """
    Search using SerpAPI and return structured results.
    """
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key:
        return None
    
    try:
        url = "https://serpapi.com/search"
        params = {
            'q': query,
            'api_key': api_key,
            'num': num_results,
            'engine': 'google'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ SerpAPI error: Status {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️ No internet connection. Please check your WiFi or network connection.")
        return None
    except requests.exceptions.Timeout:
        print(f"⚠️ Search request timed out. Please check your internet connection.")
        return None
    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return None


def extract_context_from_serp(serp_data: Dict) -> str:
    """
    Extract relevant context from SerpAPI results for RAG.
    """
    if not serp_data:
        return ""
    
    context_parts = []
    
    # Extract answer box (direct answer)
    if 'answer_box' in serp_data:
        answer_box = serp_data['answer_box']
        if 'answer' in answer_box:
            context_parts.append(f"📌 {answer_box['answer']}")
        elif 'snippet' in answer_box:
            context_parts.append(f"📌 {answer_box['snippet']}")
    
    # Extract knowledge graph
    if 'knowledge_graph' in serp_data:
        kg = serp_data['knowledge_graph']
        if 'title' in kg and 'description' in kg:
            context_parts.append(f"ℹ️ {kg['title']}: {kg['description']}")
    
    # Extract news results (for news queries)
    if 'news_results' in serp_data:
        for i, news in enumerate(serp_data['news_results'][:5], 1):
            title = news.get('title', '')
            snippet = news.get('snippet', '')
            source = news.get('source', '')
            date = news.get('date', '')
            if title:
                news_text = f"{i}. {title}"
                if snippet:
                    news_text += f" - {snippet}"
                if source:
                    news_text += f" ({source}"
                    if date:
                        news_text += f", {date}"
                    news_text += ")"
                context_parts.append(news_text)
    
    # Extract organic results (top search results)
    if 'organic_results' in serp_data and not context_parts:
        for i, result in enumerate(serp_data['organic_results'][:5], 1):
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            if title and snippet:
                context_parts.append(f"{i}. {title}: {snippet}")
    
    # Extract weather if available - PRIORITY (show first)
    if 'weather_results' in serp_data:
        weather = serp_data['weather_results']
        location = weather.get('location', '')
        temperature = weather.get('temperature', '')
        precipitation = weather.get('precipitation', '')
        humidity = weather.get('humidity', '')
        wind = weather.get('wind', '')
        weather_desc = weather.get('weather', '')
        
        if location:
            weather_text = f"🌤️ Weather in {location}:"
            if temperature:
                weather_text += f"\n   Temperature: {temperature}"
            if weather_desc:
                weather_text += f"\n   Conditions: {weather_desc}"
            if precipitation:
                weather_text += f"\n   Precipitation: {precipitation}"
            if humidity:
                weather_text += f"\n   Humidity: {humidity}"
            if wind:
                weather_text += f"\n   Wind: {wind}"
            
            # Add to the beginning of context (most important)
            context_parts.insert(0, weather_text)
    
    # Also check for weather in answer_box
    if 'answer_box' in serp_data and 'weather' in str(serp_data['answer_box']).lower():
        answer_box = serp_data['answer_box']
        if 'answer' in answer_box or 'snippet' in answer_box:
            weather_info = answer_box.get('answer', answer_box.get('snippet', ''))
            if weather_info and 'weather' not in [p.lower() for p in context_parts]:
                context_parts.insert(0, f"🌤️ {weather_info}")
    
    return "\n\n".join(context_parts)


def enhance_with_rag(prompt: str) -> tuple[str, bool]:
    """
    Enhance the prompt with real-time information if needed.
    Returns: (enhanced_prompt, rag_used)
    """
    # Check if RAG is needed
    if not should_use_rag(prompt):
        return prompt, False
    
    # Search for real-time information
    serp_results = search_serp(prompt)
    if not serp_results:
        # No internet or search failed - provide helpful offline message
        offline_prompt = f"""{prompt}

Note: I don't have access to real-time information right now because there's no internet connection. I can only provide general information based on my training data."""
        return offline_prompt, False
    
    # Extract context from search results
    context = extract_context_from_serp(serp_results)
    if not context:
        return prompt, False
    
    # Enhance prompt with context - clearer instruction to use the data
    enhanced_prompt = f"""Here is current real-time information:

{context}

Question: {prompt}

IMPORTANT: Give a direct answer using the EXACT information above. State the temperature, conditions, and details directly. Do NOT say "check the website" or "visit source" - just tell me the information."""
    
    return enhanced_prompt, True


def get_rag_status() -> Dict:
    """
    Get RAG system status.
    """
    api_key = os.getenv('SERPAPI_KEY')
    
    return {
        'enabled': api_key is not None and len(api_key) > 0,
        'api_configured': api_key is not None,
        'status': 'Ready' if api_key else 'Not Configured'
    }
