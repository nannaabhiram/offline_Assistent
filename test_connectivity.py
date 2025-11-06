"""
Test actual internet connectivity
"""
import subprocess
import socket

def test_ping():
    """Test ping to Google"""
    try:
        print("🌐 Testing ping to google.com...")
        result = subprocess.run(
            ['ping', '-n', '2', 'google.com'],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ping error: {e}")
        return False

def test_socket():
    """Test socket connection"""
    try:
        print("\n🔌 Testing socket connection to google.com:80...")
        socket.create_connection(("www.google.com", 80), timeout=5)
        print("✅ Socket connection successful")
        return True
    except Exception as e:
        print(f"❌ Socket error: {e}")
        return False

def test_dns():
    """Test DNS resolution"""
    try:
        print("\n🔍 Testing DNS resolution...")
        result = socket.getaddrinfo('google.com', 80)
        print(f"✅ DNS resolved: {result[0][4][0]}")
        return True
    except Exception as e:
        print(f"❌ DNS error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Internet Connectivity\n")
    print("=" * 50)
    
    ping_ok = test_ping()
    socket_ok = test_socket()
    dns_ok = test_dns()
    
    print("\n" + "=" * 50)
    print(f"Ping: {'✅' if ping_ok else '❌'}")
    print(f"Socket: {'✅' if socket_ok else '❌'}")
    print(f"DNS: {'✅' if dns_ok else '❌'}")
    
    if all([ping_ok, socket_ok, dns_ok]):
        print("\n🎉 Full internet connectivity confirmed!")
    else:
        print("\n⚠️ Connectivity issues detected")
