#!/usr/bin/env python3
"""
Simple Windows Volume Control
Uses Windows API to set system volume directly
"""

import sys
import subprocess
import time
from ctypes import cast, POINTER, Structure, HRESULT
from ctypes.wintypes import DWORD, BOOL

# Windows Audio API constants and structures
IID_IAudioEndpointVolume = "{5CDF2C82-841E-4546-9722-0CF74078229A}"
IID_IMMDeviceEnumerator = "{A95664D2-9614-4F35-A746-DE8DB63617E6}"
CLSID_MMDeviceEnumerator = "{BCDE0395-E52F-467C-8E3D-C4579291692E}"

class IMMDevice(Structure):
    pass

class IAudioEndpointVolume(Structure):
    pass

def set_volume(level):
    """Set Windows system volume to specific percentage"""
    try:
        # Use PowerShell to set volume via Windows Audio API
        ps_script = f'''
        try {{
            Add-Type -TypeDefinition @"
using System.Runtime.InteropServices;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {{
    int SetMasterVolumeLevelScalar(float fLevel, System.Guid eventContext);
}};
"@ -Language CSharp

            $device = New-Object -ComObject MMDeviceEnumerator
            $endpoint = $device.GetDefaultAudioEndpoint(0, 1)
            $volume = $endpoint.Activate([Guid]::Parse("5CDF2C82-841E-4546-9722-0CF74078229A"), 23, $null)
            $volume.SetMasterVolumeLevelScalar({level/100.0}, [Guid]::NewGuid()) | Out-Null
            "SUCCESS"
        }} catch {{
            "FAILED"
        }}
        '''

        result = subprocess.run(['powershell', '-Command', ps_script],
                              capture_output=True, text=True, timeout=3.0)

        if result.returncode == 0 and "SUCCESS" in result.stdout:
            print(f"Volume set to {level}%")
            return True
        else:
            print(f"PowerShell method failed: {result.stdout}")
            return False

    except Exception as e:
        print(f"Error setting volume: {e}")
        return False

def get_volume():
    """Get current Windows system volume"""
    try:
        ps_script = '''
        try {
            $device = New-Object -ComObject MMDeviceEnumerator
            $endpoint = $device.GetDefaultAudioEndpoint(0, 1)
            $volume = $endpoint.Activate([Guid]::Parse("5CDF2C82-841E-4546-9722-0CF74078229A"), 23, $null)
            $current = $volume.GetMasterVolumeLevelScalar()
            Write-Host ([math]::Round($current * 100))
        } catch {
            Write-Host "ERROR"
        }
        '''

        result = subprocess.run(['powershell', '-Command', ps_script],
                              capture_output=True, text=True, timeout=3.0)

        if result.returncode == 0 and "ERROR" not in result.stdout:
            try:
                return int(float(result.stdout.strip()))
            except:
                return None
        return None

    except Exception as e:
        print(f"Error getting volume: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: volume_control.py [get|set LEVEL]")
        sys.exit(1)

    action = sys.argv[1]

    if action == "get":
        volume = get_volume()
        if volume is not None:
            print(f"Current volume: {volume}%")
        else:
            print("Could not get volume")

    elif action == "set":
        if len(sys.argv) < 3:
            print("Usage: volume_control.py set LEVEL")
            sys.exit(1)

        try:
            level = int(sys.argv[2])
            if 0 <= level <= 100:
                if set_volume(level):
                    print(f"Successfully set volume to {level}%")
                else:
                    print(f"Failed to set volume to {level}%")
            else:
                print("Volume level must be between 0 and 100")
        except ValueError:
            print("Volume level must be a number")

    else:
        print("Invalid action. Use 'get' or 'set'")
