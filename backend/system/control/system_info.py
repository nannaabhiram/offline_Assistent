"""
System Information Control Module
Handles system monitoring and information retrieval
"""
import psutil
import platform
from typing import Dict, Any


def get_cpu_usage() -> Dict[str, Any]:
    """Get CPU usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        return {
            'success': True,
            'cpu_percent': cpu_percent,
            'cpu_count': cpu_count,
            'message': f'CPU usage: {cpu_percent}% ({cpu_count} cores)'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get CPU usage: {str(e)}'
        }


def get_memory_info() -> Dict[str, Any]:
    """Get memory information"""
    try:
        mem = psutil.virtual_memory()
        return {
            'success': True,
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'message': f'Memory: {mem.percent}% used ({round(mem.used / (1024**3), 2)} GB / {round(mem.total / (1024**3), 2)} GB)'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get memory info: {str(e)}'
        }


def get_disk_info(path: str = 'C:\\') -> Dict[str, Any]:
    """Get disk usage"""
    try:
        disk = psutil.disk_usage(path)
        return {
            'success': True,
            'path': path,
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'message': f'Disk {path}: {disk.percent}% used ({round(disk.free / (1024**3), 2)} GB free)'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get disk info: {str(e)}',
            'path': path
        }


def get_battery_status() -> Dict[str, Any]:
    """Get battery status"""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return {
                'success': False,
                'message': 'No battery detected (desktop PC)',
                'has_battery': False
            }
        
        return {
            'success': True,
            'has_battery': True,
            'percent': battery.percent,
            'plugged_in': battery.power_plugged,
            'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
            'message': f'Battery: {battery.percent}% {"(charging)" if battery.power_plugged else "(on battery)"}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get battery status: {str(e)}'
        }


def get_os_info() -> Dict[str, Any]:
    """Get OS information"""
    try:
        return {
            'success': True,
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'platform': platform.platform(),
            'message': f'OS: {platform.platform()}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get OS info: {str(e)}'
        }


def get_network_info() -> Dict[str, Any]:
    """Get network information"""
    try:
        net_io = psutil.net_io_counters()
        return {
            'success': True,
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'message': f'Network: {round(net_io.bytes_recv / (1024**2), 2)} MB received, {round(net_io.bytes_sent / (1024**2), 2)} MB sent'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get network info: {str(e)}'
        }


def get_full_system_status() -> Dict[str, Any]:
    """Get complete system status"""
    try:
        return {
            'success': True,
            'cpu': get_cpu_usage(),
            'memory': get_memory_info(),
            'disk': get_disk_info(),
            'battery': get_battery_status(),
            'os': get_os_info(),
            'network': get_network_info()
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get system status: {str(e)}'
        }
