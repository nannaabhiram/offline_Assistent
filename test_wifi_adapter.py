"""
Test WiFi adapter detection
"""
import subprocess

def get_wifi_interface_name():
    """Get the WiFi interface name on Windows"""
    try:
        # List all network interfaces
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print("=== Network Interfaces ===")
        print(result.stdout)
        print("=" * 50)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            wifi_interfaces = []
            
            # Look for wireless/WiFi interfaces
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['wi-fi', 'wireless', 'wlan']):
                    print(f"Found WiFi line: {line}")
                    # Extract interface name (usually the last column)
                    parts = line.split()
                    if len(parts) >= 4:
                        # Get the interface name (last part)
                        interface_name = ' '.join(parts[3:]).strip()
                        wifi_interfaces.append(interface_name)
                        print(f"  -> Extracted name: {interface_name}")
            
            if wifi_interfaces:
                print(f"\n✅ Found WiFi interfaces: {wifi_interfaces}")
                return wifi_interfaces[0]
            else:
                print("\n⚠️ No WiFi interfaces found, using default")
        
        # Common interface names to try
        common_names = ['Wi-Fi', 'WiFi', 'Wireless', 'WLAN', 'Wireless Network Connection']
        return common_names[0]  # Default to Wi-Fi
        
    except Exception as e:
        print(f"❌ Error getting WiFi interface: {e}")
        return 'Wi-Fi'  # Default fallback


def check_wifi_details():
    """Show detailed WiFi information"""
    try:
        print("\n=== WLAN Interfaces ===")
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("🔍 Testing WiFi Adapter Detection\n")
    
    wifi_name = get_wifi_interface_name()
    print(f"\n📡 Detected WiFi Interface: '{wifi_name}'")
    
    check_wifi_details()
