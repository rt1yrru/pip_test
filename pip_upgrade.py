import subprocess
import sys
import platform
import ujson as json

class Color:
    BLUE = '\033[94m'    # Initializing / Checking
    VIOLET = '\033[95m'  # Upgrade needed
    GREEN = '\033[92m'   # Success
    RED = '\033[91m'     # Error
    ORANGE = '\033[33m'  # Didn't change
    BOLD = '\033[1m'
    END = '\033[0m'

def run_cmd(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def update_manager():
    # 1. Detect OS
    print(f"{Color.BLUE}[*] Initializing... OS Detected: {platform.system()}{Color.END}")

    # 2. Show All Available Packages (Installed)
    print(f"\n{Color.BOLD}--- CURRENTLY INSTALLED PACKAGES ---{Color.END}")
    all_packages_cmd = run_cmd(f"{sys.executable} -m pip list --format=json")
    
    if all_packages_cmd.returncode == 0:
        all_pkgs = json.loads(all_packages_cmd.stdout)
        print(f"{'Package':<30} {'Version':<15}")
        print("-" * 45)
        for pkg in all_pkgs:
            # We show these in Blue to indicate they are being 'read'
            print(f"{Color.BLUE}{pkg['name']:<30}{Color.END} {pkg['version']:<15}")
    print("-" * 45 + "\n")

    # 3. Check for Pip's own upgrade
    print(f"{Color.BLUE}[*] Checking if pip needs an upgrade...{Color.END}")
    check_pip = run_cmd(f"{sys.executable} -m pip list --limit-action=1")
    
    if "version" in check_pip.stderr and "available" in check_pip.stderr:
        print(f"{Color.VIOLET}[!] Pip upgrade available! Upgrading now...{Color.END}")
        up_pip = run_cmd(f"{sys.executable} -m pip install --upgrade pip")
        if up_pip.returncode == 0:
            print(f"{Color.GREEN}[✓] Pip upgraded successfully.{Color.END}")
        else:
            print(f"{Color.RED}[X] Pip upgrade failed.{Color.END}")
    else:
        print(f"{Color.ORANGE}[-] Pip version didn't change (already up to date).{Color.END}")

    # 4. Check for Outdated Packages
    print(f"{Color.BLUE}[*] Checking for updates for other packages...{Color.END}")
    list_outdated = run_cmd(f"{sys.executable} -m pip list --outdated --format=json")
    
    try:
        packages = json.loads(list_outdated.stdout)
        if not packages:
            print(f"{Color.ORANGE}[-] All other packages are already up to date.{Color.END}")
            return

        for pkg in packages:
            name = pkg['name']
            current_v = pkg['version']
            latest_v = pkg['latest_version']
            
            print(f"{Color.VIOLET}[!] Upgrade needed: {name} ({current_v} -> {latest_v}){Color.END}")
            
            # Executing upgrade
            upgrade_res = run_cmd(f"{sys.executable} -m pip install --upgrade {name} --break-system-packages")
            
            if upgrade_res.returncode == 0:
                print(f"{Color.GREEN}[✓] {name} successfully upgraded.{Color.END}")
            else:
                print(f"{Color.RED}[X] Failed to upgrade {name}.{Color.END}")

    except json.JSONDecodeError:
        print(f"{Color.RED}[X] Error: Could not read package list.{Color.END}")
        print(f"{Color.BLUE}[*] Attempting pip repair...{Color.END}")
        run_cmd(f"{sys.executable} -m ensurepip --upgrade")

if __name__ == "__main__":
    update_manager()
