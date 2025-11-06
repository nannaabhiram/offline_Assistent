"""
Mouse & Keyboard Input Control Module
Handles GUI automation
"""
from typing import Dict, Any, Tuple

# Try to import pyautogui
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def is_available() -> bool:
    """Check if pyautogui is available"""
    return PYAUTOGUI_AVAILABLE


def move_mouse(x: int, y: int) -> Dict[str, Any]:
    """Move mouse to coordinates"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed. Install with: pip install pyautogui'
        }
    
    try:
        pyautogui.moveTo(x, y)
        return {
            'success': True,
            'message': f'Moved mouse to ({x}, {y})',
            'x': x,
            'y': y
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to move mouse: {str(e)}'
        }


def click_mouse(button: str = 'left') -> Dict[str, Any]:
    """Click mouse button"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        pyautogui.click(button=button)
        return {
            'success': True,
            'message': f'{button} mouse button clicked',
            'button': button
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to click: {str(e)}'
        }


def type_text(text: str, interval: float = 0.1) -> Dict[str, Any]:
    """Type text"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        pyautogui.write(text, interval=interval)
        return {
            'success': True,
            'message': f'Typed: {text[:50]}...' if len(text) > 50 else f'Typed: {text}',
            'length': len(text)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to type: {str(e)}'
        }


def press_key(key: str) -> Dict[str, Any]:
    """Press a keyboard key"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        pyautogui.press(key)
        return {
            'success': True,
            'message': f'Pressed key: {key}',
            'key': key
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to press key: {str(e)}'
        }


def get_mouse_position() -> Dict[str, Any]:
    """Get current mouse position"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        x, y = pyautogui.position()
        return {
            'success': True,
            'x': x,
            'y': y,
            'position': f'({x}, {y})'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get position: {str(e)}'
        }


def get_screen_size() -> Dict[str, Any]:
    """Get screen dimensions"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        width, height = pyautogui.size()
        return {
            'success': True,
            'width': width,
            'height': height,
            'resolution': f'{width}x{height}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get screen size: {str(e)}'
        }
