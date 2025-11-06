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
            print(f"SerpAPI error: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"SerpAPI search error: {e}")
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
            context_parts.append(f"Direct Answer: {answer_box['answer']}")
        elif 'snippet' in answer_box:
            context_parts.append(f"Answer: {answer_box['snippet']}")
    
    # Extract knowledge graph
    if 'knowledge_graph' in serp_data:
        kg = serp_data['knowledge_graph']
        if 'title' in kg and 'description' in kg:
            context_parts.append(f"{kg['title']}: {kg['description']}")
    
    # Extract organic results (top search results)
    if 'organic_results' in serp_data:
        for i, result in enumerate(serp_data['organic_results'][:3], 1):
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            if title and snippet:
                context_parts.append(f"Source {i}: {snippet}")
    
    # Extract weather if available
    if 'weather_results' in serp_data:
        weather = serp_data['weather_results']
        location = weather.get('location', '')
        temperature = weather.get('temperature', '')
        weather_info = weather.get('weather', '')
        if location and temperature:
            context_parts.append(f"Weather in {location}: {temperature}, {weather_info}")
    
    return "\n".join(context_parts)


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
        return prompt, False
    
    # Extract context from search results
    context = extract_context_from_serp(serp_results)
    if not context:
        return prompt, False
    
    # Enhance prompt with context - clearer instruction to use the data
    enhanced_prompt = f"""You have access to the following real-time information from the internet:

{context}

User's question: {prompt}

Please provide a direct and helpful answer using the real-time information above. Do not suggest checking other sources - give the answer based on the data provided."""
    
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
