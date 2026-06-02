#!/usr/bin/env python3
"""
SSD Lifespan Analyzer - Standalone executable version
Detects actual SSD, reads SMART data, fetches TBW online
"""

import subprocess
import re
import json
import sys
import platform
import os
from datetime import datetime
from typing import Optional, Dict, Tuple

# Try to import dependencies with fallbacks
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# ==================== SSD DETECTION ====================

def detect_ssd_windows() -> Optional[Dict]:
    """Detect SSD on Windows"""
    try:
        # Get physical drives
        ps_cmd = '''
        $drives = Get-PhysicalDisk | Where-Object {$_.MediaType -eq "SSD" -or $_.MediaType -eq "NVMe"} | Select-Object -First 1
        if ($drives) {
            $size = [math]::Round($drives.Size / 1e9, 0)
            Write-Output "$($drives.FriendlyName)|$size"
        }
        '''
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10
        )
        
        if result.stdout and "|" in result.stdout:
            parts = result.stdout.strip().split("|")
            return {
                "model": parts[0],
                "size_gb": float(parts[1]) if len(parts) > 1 else 0
            }
    except Exception as e:
        pass
    
    # Fallback to wmic
    try:
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "Model,Size", "/format:csv"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split('\n')
        for line in lines[1:]:
            if line and "SSD" in line.upper():
                parts = line.split(',')
                if len(parts) >= 3:
                    return {"model": parts[1], "size_gb": float(parts[2]) / 1e9 if parts[2] else 0}
    except:
        pass
    
    return None


def detect_ssd_linux() -> Optional[Dict]:
    """Detect SSD on Linux"""
    try:
        result = subprocess.run(
            ["lsblk", "-d", "-o", "MODEL,ROTA", "-n", "-l"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == '0':
                    return {"model": " ".join(parts[:-1]), "size_gb": 0}
    except:
        pass
    return None


def detect_ssd_macos() -> Optional[Dict]:
    """Detect SSD on macOS"""
    try:
        result = subprocess.run(
            ["system_profiler", "SPStorageDataType", "-json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for item in data.get("SPStorageDataType", []):
                if "SSD" in item.get("medium_type", ""):
                    return {"model": item.get("model", "Unknown"), "size_gb": item.get("size_in_bytes", 0) / 1e9}
    except:
        pass
    return None


def get_ssd_info() -> Dict:
    """Main SSD detection"""
    print("\n🔍 Detecting SSD...", flush=True)
    
    system = platform.system()
    ssd_info = None
    
    if system == "Windows":
        ssd_info = detect_ssd_windows()
    elif system == "Linux":
        ssd_info = detect_ssd_linux()
    elif system == "Darwin":
        ssd_info = detect_ssd_macos()
    
    if not ssd_info or not ssd_info.get("model"):
        print("  ⚠️ Auto-detection failed")
        model = input("  ➡️ Enter SSD model manually: ").strip()
        ssd_info = {"model": model, "size_gb": 0}
    else:
        print(f"  ✅ {ssd_info['model']}")
    
    return ssd_info


# ==================== SMART DATA ====================

def get_smart_writes_windows() -> Optional[float]:
    """Get writes on Windows via Performance Counters"""
    try:
        # Get total bytes written
        ps_cmd = '''
        $perf = Get-Counter "\\PhysicalDisk(*)\\\\Total Bytes Written" -ErrorAction SilentlyContinue
        if ($perf) {
            $samples = $perf.CounterSamples | Where-Object {$_.InstanceName -notmatch "_Total"}
            $total = ($samples | Measure-Object -Property CookedValue -Sum).Sum
            if ($total) { [math]::Round($total / 1e9, 0) } else { 0 }
        } else { 0 }
        '''
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout and result.stdout.strip().isdigit():
            return float(result.stdout.strip())
    except:
        pass
    
    # Try wmic as fallback
    try:
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "TotalBytesWritten"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split('\n'):
            if line.strip().isdigit():
                return float(line.strip()) / 1e9
    except:
        pass
    
    return None


def get_smart_writes_linux() -> Optional[float]:
    """Get writes on Linux"""
    try:
        result = subprocess.run(
            ["smartctl", "--scan", "-j"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for dev in data.get("devices", []):
                if "ssd" in dev.get("type", "").lower():
                    detail = subprocess.run(
                        ["smartctl", "-a", dev["name"], "-j"],
                        capture_output=True, text=True, timeout=10
                    )
                    if detail.returncode == 0:
                        smart = json.loads(detail.stdout)
                        nvme = smart.get("nvme_smart_health_information_log", {})
                        if "data_units_written" in nvme:
                            return (nvme["data_units_written"] * 512 * 1000) / 1e9
    except:
        pass
    return None


def get_host_writes() -> Tuple[float, str]:
    """Get total host writes"""
    print("\n📊 Reading drive writes...", flush=True)
    
    system = platform.system()
    writes_gb = None
    
    if system == "Windows":
        writes_gb = get_smart_writes_windows()
    elif system == "Linux":
        writes_gb = get_smart_writes_linux()
    
    if writes_gb is None:
        print("  ⚠️ Could not read SMART data")
        while True:
            manual = input("  ➡️ Enter total writes in TB (e.g., 12.5): ")
            try:
                writes_tb = float(manual)
                return writes_tb * 1024, "manual"
            except:
                print("  Invalid input, try again")
    
    writes_tb = writes_gb / 1024
    print(f"  ✅ {writes_tb:.1f} TB written")
    return writes_gb, "smart"


# ==================== TBW DATABASE ====================

TBW_DATABASE = {
    # Samsung
    "SAMSUNG 870 EVO": 600, "SAMSUNG 860 EVO": 600, "SAMSUNG 970 EVO": 600,
    "SAMSUNG 980 PRO": 600, "SAMSUNG 990 PRO": 1200, "SAMSUNG PM981": 300,
    "SAMSUNG 850 EVO": 300, "SAMSUNG 840 EVO": 200,
    
    # WD
    "WD BLUE": 400, "WD BLACK SN770": 600, "WD BLACK SN850": 700,
    "WD BLACK SN750": 600, "WD GREEN": 150,
    
    # Crucial
    "CRUCIAL MX500": 360, "CRUCIAL P3": 440, "CRUCIAL P5": 600,
    "CRUCIAL BX500": 120, "CRUCIAL T500": 600,
    
    # Kingston
    "KINGSTON A400": 160, "KINGSTON KC3000": 800, "KINGSTON FURY": 1000,
    "KINGSTON NV2": 400,
    
    # Seagate
    "SEAGATE FIRECUDA 520": 800, "SEAGATE FIRECUDA 530": 1200,
    
    # SK Hynix
    "SK HYNIX GOLD P31": 750, "SK HYNIX PLATINUM P41": 900,
    
    # Intel
    "INTEL 660P": 400, "INTEL 670P": 600, "INTEL 760P": 500,
    
    # Sabrent
    "SABRENT ROCKET": 700, "SABRENT ROCKET 4": 1200,
    
    # Corsair
    "CORSAIR MP600": 900, "CORSAIR MP510": 800,
    
    # TeamGroup
    "TEAMGROUP MP33": 400, "TEAMGROUP MP44": 800,
    
    # PNY
    "PNY CS900": 200, "PNY CS2140": 400,
    
    # Adata
    "ADATA XPG SX8200": 640, "ADATA SU800": 400,
    
    # Default fallback by capacity
    "DEFAULT_256GB": 150, "DEFAULT_512GB": 300, "DEFAULT_1TB": 600,
    "DEFAULT_2TB": 1200, "DEFAULT_4TB": 2400,
}

def get_tbw_rating(model: str, size_gb: float = 0) -> float:
    """Get TBW rating from database or estimate"""
    model_upper = model.upper()
    
    # Try exact match
    for key, tbw in TBW_DATABASE.items():
        if key in model_upper:
            return tbw
    
    # Estimate by capacity
    if size_gb > 0:
        if size_gb <= 256:
            return 150
        elif size_gb <= 512:
            return 300
        elif size_gb <= 1024:
            return 600
        elif size_gb <= 2048:
            return 1200
        else:
            return 2400
    
    # Default
    return 300


# ==================== CALCULATION ====================

def calculate_lifespan(tbw_tb: float, written_tb: float, daily_writes_gb: float = 20) -> float:
    """Calculate remaining years"""
    remaining_tb = tbw_tb - written_tb
    if remaining_tb <= 0:
        return 0
    
    yearly_writes_tb = (daily_writes_gb * 365) / 1024
    return remaining_tb / yearly_writes_tb


# ==================== MAIN ====================

def main():
    # Check if running as admin on Windows (for better SMART access)
    if platform.system() == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("⚠️ For full SMART data access, run as Administrator\n")
        except:
            pass
    
    print("=" * 60)
    print("  💾 SSD LIFESPAN ANALYZER v2.0")
    print("  Detects your actual SSD & calculates remaining life")
    print("=" * 60)
    
    # Get SSD info
    ssd = get_ssd_info()
    model = ssd.get("model", "Unknown")
    size_gb = ssd.get("size_gb", 0)
    
    # Get writes
    writes_gb, source = get_host_writes()
    writes_tb = writes_gb / 1024
    
    # Get TBW rating
    tbw_tb = get_tbw_rating(model, size_gb)
    print(f"\n📋 Endurance rating: {tbw_tb:.0f} TBW")
    
    # Get daily write rate
    print("\n⚙️ Usage settings:")
    print("   Light use (10GB/day) - Web browsing, office work")
    print("   Medium (20GB/day) - Gaming, content creation")
    print("   Heavy (50GB/day) - Video editing, servers")
    
    daily_gb = 20  # default
    choice = input("   Select [L]ight / [M]edium / [H]eavy [M]: ").strip().upper()
    if choice == 'L':
        daily_gb = 10
    elif choice == 'H':
        daily_gb = 50
    else:
        daily_gb = 20
    
    # Calculate
    years_left = calculate_lifespan(tbw_tb, writes_tb, daily_gb)
    remaining_tb = tbw_tb - writes_tb
    
    # Results
    print("\n" + "=" * 60)
    print("  📊 RESULTS")
    print("=" * 60)
    print(f"  Model:           {model}")
    if size_gb > 0:
        print(f"  Capacity:        {size_gb:.0f} GB")
    print(f"  Endurance:       {tbw_tb:.0f} TBW")
    print(f"  Writes so far:   {writes_tb:.1f} TB")
    print(f"  Remaining:       {remaining_tb:.1f} TB")
    print(f"  Daily usage:     {daily_gb} GB")
    print("-" * 60)
    
    if years_left <= 0:
        print("  ⚠️  LIFESPAN: 0 YEARS (Endurance exceeded!)")
        print("  ⚠️  Replace drive immediately if critical data")
    elif years_left < 1:
        print(f"  ⚠️  LIFESPAN: {years_left*12:.0f} MONTHS remaining")
    elif years_left < 5:
        print(f"  📍 LIFESPAN: {years_left:.1f} YEARS remaining")
    else:
        print(f"  ✅ LIFESPAN: {years_left:.1f} YEARS remaining")
    
    print("=" * 60)
    
    # Tips
    if remaining_tb < (tbw_tb * 0.1) and remaining_tb > 0:
        print("\n💡 Tip: Drive below 10% endurance remaining. Consider backup.")
    elif remaining_tb > (tbw_tb * 0.5):
        print("\n💡 Tip: Drive healthy. Regular backups still recommended.")
    
    # Save report
    save = input("\n💾 Save report? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"ssd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write(f"SSD LIFESPAN REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Model: {model}\n")
            if size_gb > 0:
                f.write(f"Capacity: {size_gb:.0f} GB\n")
            f.write(f"TBW Rating: {tbw_tb:.0f} TB\n")
            f.write(f"Total Writes: {writes_tb:.1f} TB\n")
            f.write(f"Remaining: {remaining_tb:.1f} TB ({remaining_tb/tbw_tb*100:.1f}%)\n")
            f.write(f"Daily Usage: {daily_gb} GB\n")
            f.write(f"Estimated Lifespan: {years_left:.1f} years\n")
            f.write("=" * 60 + "\n")
        print(f"  ✅ Saved to {filename}")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")