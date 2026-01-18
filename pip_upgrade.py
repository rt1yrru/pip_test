import subprocess
import sys
import platform
import ujson as json
import datetime
import socket

class Color:
    BLUE = '\033[94m'    # Initializing
    VIOLET = '\033[95m'  # Upgrade needed
    GREEN = '\033[92m'   # Success
    RED = '\033[91m'     # Error
    ORANGE = '\033[33m'  # No change / No Internet
    BOLD = '\033[1m'
    END = '\033[0m'

def check_internet():
    """Checks if the device has an active internet connection."""
    try:
        # Connect to Google's DNS (8.8.8.8) on port 53
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def run_cmd(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def update_manager():
    log_content = []
    log_content.append(f"Update Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Network Test
    print(f"{Color.BLUE}[*] Checking network connectivity...{Color.END}")
    if not check_internet():
        print(f"{Color.ORANGE}[!] No internet. Skipping online updates.{Color.END}")
        log_content.append("[Status] Aborted: No internet connection.")
        # Proceeding to list local packages only
    else:
        print(f"{Color.GREEN}[✓] Internet connected.{Color.END}")

    # 2. OS Detection
    print(f"{Color.BLUE}[*] Initializing... OS Detected: {platform.system()}{Color.END}")

    # 3. Show & Log All Local Packages
    print(f"\n{Color.BOLD}--- CURRENTLY INSTALLED PACKAGES ---{Color.END}")
    all_packages_cmd = run_cmd(f"{sys.executable} -m pip list --format=json")
    
    if all_packages_cmd.returncode == 0:
        all_pkgs = json.loads(all_packages_cmd.stdout)
        header = f"{'Package':<30} {'Version':<15}"
        print(header)
        log_content.append("\nInstalled Packages:\n" + header)
        print("-" * 45)
        for pkg in all_pkgs:
            print(f"{Color.BLUE}{pkg['name']:<30}{Color.END} {pkg['version']:<15}")
            log_content.append(f"{pkg['name']:<30} {pkg['version']:<15}")

    # Stop here if no internet
    if not check_internet():
        with open("package_report.txt", "w") as f:
            f.write("\n".join(log_content))
        return

    # 4. Upgrade Pip
    print(f"\n{Color.BLUE}[*] Checking pip version...{Color.END}")
    check_pip = run_cmd(f"{sys.executable} -m pip list --limit-action=1")
    if "version" in check_pip.stderr and "available" in check_pip.stderr:
        print(f"{Color.VIOLET}[!] Upgrading Pip...{Color.END}")
        run_cmd(f"{sys.executable} -m pip install --upgrade pip")
    else:
        print(f"{Color.ORANGE}[-] Pip is already up to date.{Color.END}")

    # 5. Upgrade Outdated Packages
    print(f"{Color.BLUE}[*] Scanning for outdated packages...{Color.END}")
    list_outdated = run_cmd(f"{sys.executable} -m pip list --outdated --format=json")
    
    try:
        outdated_pkgs = json.loads(list_outdated.stdout)
        if outdated_pkgs:
            for pkg in outdated_pkgs:
                name = pkg['name']
                print(f"{Color.VIOLET}[!] Upgrading {name}...{Color.END}")
                res = run_cmd(f"{sys.executable} -m pip install --upgrade {name} --break-system-packages")
                if res.returncode == 0:
                    print(f"{Color.GREEN}[✓] Successfully upgraded {name}{Color.END}")
                    log_content.append(f"[Upgrade] {name}: Success")
                else:
                    print(f"{Color.RED}[X] Failed to upgrade {name}{Color.END}")
        else:
            print(f"{Color.ORANGE}[-] All packages are up to date.{Color.END}")
    except:
        print(f"{Color.RED}[X] Error scanning packages.{Color.END}")

    # 6. Maintenance & Clean Cache
    print(f"\n{Color.BLUE}[*] Cleaning pip cache...{Color.END}")
    run_cmd(f"{sys.executable} -m pip cache purge")
    print(f"{Color.GREEN}[✓] Maintenance complete.{Color.END}")

    # 7. Final Export
    with open("package_report.txt", "w") as f:
        f.write("\n".join(log_content))
    print(f"\n{Color.GREEN}[✓] Final report saved to 'package_report.txt'{Color.END}")

if __name__ == "__main__":
    update_manager()
