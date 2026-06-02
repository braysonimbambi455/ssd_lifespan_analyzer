#!/usr/bin/env python3
"""
SSD Lifespan Analyzer - Complete Local Tool
Detects actual SSD, calculates lifespan
"""

import subprocess
import sys
import os
import platform
from datetime import datetime
from typing import Optional, Dict

def detect_ssd_windows() -> Optional[Dict]:
    """Detect SSD on Windows"""
    try:
        ps_cmd = '''
        $drives = Get-PhysicalDisk | Where-Object {$_.MediaType -eq "SSD" -or $_.MediaType -eq "NVMe"} | Select-Object -First 1
        if ($drives) {
            $size = [math]::Round($drives.Size / 1e9, 0)
            Write-Output "$($drives.FriendlyName)|$size"
        }
        '''
        result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, timeout=10)
        if result.stdout and "|" in result.stdout:
            parts = result.stdout.strip().split("|")
            return {"model": parts[0], "size_gb": float(parts[1]) if len(parts) > 1 else 0}
    except Exception:
        pass
    return None

def get_ssd_info() -> Dict:
    """Main SSD detection"""
    print("\n" + "=" * 60)
    print("  🔍 DETECTING SSD HARDWARE")
    print("=" * 60)
    
    system = platform.system()
    ssd_info = None
    
    if system == "Windows":
        print("  Running Windows detection...")
        ssd_info = detect_ssd_windows()
    
    if not ssd_info or not ssd_info.get("model"):
        print("\n  ⚠️ Could not auto-detect SSD")
        print("  Enter your SSD model manually (e.g., Samsung 980 Pro, WD Blue)")
        model = input("\n  ➡️ SSD Model: ").strip()
        if not model:
            model = "Unknown SSD"
        ssd_info = {"model": model, "size_gb": 0}
    else:
        print(f"\n  ✅ Detected: {ssd_info['model']}")
        if ssd_info.get('size_gb', 0) > 0:
            print(f"  📀 Capacity: {ssd_info['size_gb']:.0f} GB")
    
    return ssd_info

# TBW Database
TBW_DB = {
    "SAMSUNG 870 EVO": 600, "SAMSUNG 860 EVO": 600, "SAMSUNG 970 EVO": 600,
    "SAMSUNG 980 PRO": 600, "SAMSUNG 990 PRO": 1200, "SAMSUNG 850 EVO": 300,
    "WD BLUE": 400, "WD BLACK SN770": 600, "WD BLACK SN850": 700,
    "CRUCIAL MX500": 360, "CRUCIAL P3": 440, "CRUCIAL P5": 600,
    "KINGSTON A400": 160, "KINGSTON KC3000": 800, "KINGSTON FURY": 1000,
    "SEAGATE FIRECUDA 520": 800, "SK HYNIX GOLD P31": 750,
    "INTEL 660P": 400, "INTEL 670P": 600, "SABRENT ROCKET": 700,
    "CORSAIR MP600": 900, "TEAMGROUP MP33": 400, "PNY CS900": 200,
}

def get_tbw(model: str, size_gb: float = 0) -> float:
    """Get TBW rating from database or estimate"""
    model_upper = model.upper()
    
    for key, tbw in TBW_DB.items():
        if key in model_upper:
            return tbw
    
    # Estimate by capacity
    if size_gb > 0:
        if size_gb <= 256: return 150
        elif size_gb <= 512: return 300
        elif size_gb <= 1024: return 600
        elif size_gb <= 2048: return 1200
        else: return 2400
    
    # Default fallback
    return 300

def main():
    # Get the script's directory for saving reports
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("  💾 SSD LIFESPAN ANALYZER")
    print("  Estimate remaining life of your SSD")
    print("=" * 60)
    print(f"\n  📁 Script location: {script_dir}")
    
    # Step 1: Detect SSD
    ssd = get_ssd_info()
    model = ssd.get("model", "Unknown")
    size_gb = ssd.get("size_gb", 0)
    
    # Step 2: Get TBW rating
    tbw = get_tbw(model, size_gb)
    print(f"\n  📋 Endurance Rating: {tbw} TBW")
    print(f"     (Total Bytes Written - manufacturer warranty limit)")
    
    # Step 3: Get writes so far
    print("\n" + "=" * 60)
    print("  📊 HOST WRITES INPUT")
    print("=" * 60)
    print("  Enter total data written to your SSD so far.")
    print("  If unknown, you can:")
    print("    - Install CrystalDiskInfo to check")
    print("    - Check your SSD manufacturer's software")
    print("    - Enter 0 if you don't know")
    print()
    
    while True:
        try:
            writes_input = input("  ➡️ Total writes so far (in TB, e.g., 12.5): ")
            if not writes_input:
                writes_tb = 0
                print("  ℹ️ Assuming 0 TB written")
                break
            writes_tb = float(writes_input)
            if writes_tb < 0:
                print("  ❌ Please enter a positive number")
                continue
            break
        except ValueError:
            print("  ❌ Invalid input. Please enter a number (e.g., 12.5)")
    
    # Step 4: Usage pattern
    print("\n" + "=" * 60)
    print("  ⚙️ USAGE PATTERN")
    print("=" * 60)
    print("  Select your typical daily write amount:")
    print("    [1] Light (10 GB/day) - Web browsing, office work")
    print("    [2] Medium (20 GB/day) - Gaming, content creation")
    print("    [3] Heavy (50 GB/day) - Video editing, servers")
    print("    [4] Custom - Enter your own value")
    print()
    
    while True:
        choice = input("  ➡️ Enter choice (1-4) [2]: ").strip()
        if choice == "":
            daily_gb = 20
            break
        elif choice == "1":
            daily_gb = 10
            break
        elif choice == "2":
            daily_gb = 20
            break
        elif choice == "3":
            daily_gb = 50
            break
        elif choice == "4":
            try:
                daily_gb = float(input("  ➡️ Enter daily writes in GB: "))
                if daily_gb > 0:
                    break
                else:
                    print("  ❌ Please enter a positive number")
            except ValueError:
                print("  ❌ Invalid input")
        else:
            print("  ❌ Invalid choice. Enter 1, 2, 3, or 4")
    
    # Step 5: Calculate
    remaining_tb = tbw - writes_tb
    yearly_writes_tb = (daily_gb * 365) / 1024
    
    if yearly_writes_tb > 0 and remaining_tb > 0:
        years_left = remaining_tb / yearly_writes_tb
    else:
        years_left = 0
    
    # Step 6: Display results
    print("\n" + "=" * 60)
    print("  📊 RESULTS")
    print("=" * 60)
    print(f"  SSD Model:        {model}")
    print(f"  Endurance (TBW):  {tbw} TB")
    print(f"  Writes so far:    {writes_tb:.1f} TB")
    print(f"  Remaining TBW:    {remaining_tb:.1f} TB")
    print(f"  Daily usage:      {daily_gb} GB/day")
    print(f"  Yearly writes:    {yearly_writes_tb:.1f} TB/year")
    print("-" * 60)
    
    if remaining_tb <= 0:
        print("  ⚠️  STATUS: ENDURANCE EXCEEDED!")
        print("  ⚠️  Your SSD has exceeded its rated endurance.")
        print("  ⚠️  Consider backing up data and replacing the drive.")
    elif years_left < 1:
        print(f"  ⚠️  ESTIMATED LIFESPAN: {years_left * 12:.0f} MONTHS")
    elif years_left < 3:
        print(f"  📍 ESTIMATED LIFESPAN: {years_left:.1f} YEARS")
    elif years_left < 10:
        print(f"  ✅ ESTIMATED LIFESPAN: {years_left:.1f} YEARS")
    else:
        print(f"  ✅ ESTIMATED LIFESPAN: {years_left:.1f} YEARS (Excellent health)")
    
    print("=" * 60)
    
    # Health assessment
    print("\n  💡 HEALTH ASSESSMENT:")
    if remaining_tb > tbw * 0.8:
        print("     ✅ Excellent - Drive is nearly new")
    elif remaining_tb > tbw * 0.5:
        print("     ✅ Good - Drive has plenty of life left")
    elif remaining_tb > tbw * 0.2:
        print("     ⚠️ Moderate - Consider monitoring writes")
    elif remaining_tb > 0:
        print("     ⚠️ Low - Drive approaching end of warranty life")
    else:
        print("     ❌ Critical - Replace drive soon")
    
    # Tips
    print("\n  💡 TIPS TO EXTEND SSD LIFE:")
    print("     • Move temp files to HDD")
    print("     • Reduce browser cache size")
    print("     • Disable hibernation if not needed")
    print("     • Keep 20% free space for wear leveling")
    
    # Save report
    print("\n" + "-" * 60)
    save = input("  💾 Save report to file? (y/n): ").strip().lower()
    if save == 'y' or save == 'yes':
        filename = os.path.join(script_dir, f"ssd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write(f"SSD LIFESPAN REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 60 + "\n")
            f.write(f"SSD Model: {model}\n")
            f.write(f"TBW Rating: {tbw} TB\n")
            f.write(f"Total Writes: {writes_tb:.1f} TB\n")
            f.write(f"Remaining TBW: {remaining_tb:.1f} TB\n")
            f.write(f"Daily Usage: {daily_gb} GB/day\n")
            f.write(f"Estimated Lifespan: {years_left:.1f} years\n")
            f.write("=" * 60 + "\n")
        print(f"  ✅ Report saved to: {filename}")
    
    print("\n" + "=" * 60)
    print("  Thank you for using SSD Lifespan Analyzer!")
    print("=" * 60)
    input("\n  Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Cancelled by user.")
        input("\n  Press Enter to exit...")
    except Exception as e:
        print(f"\n  ❌ Unexpected error: {e}")
        input("\n  Press Enter to exit...")