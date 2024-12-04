import os
import sys
import subprocess
import winreg as reg
import requests
import shutil

# Paths
HOMEDRIVE = os.environ['HOMEDRIVE']
HSHARP_DIR = os.path.join(HOMEDRIVE, "HSharp")
ICONS_DIR = os.path.join(HSHARP_DIR, "icons")
ICON_PATH = os.path.join(ICONS_DIR, "hs_icon.png")

# GitHub version check URL
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Hxolotl15/HSharp/main/version.txt"

def create_hsharp_directory():
    os.makedirs(ICONS_DIR, exist_ok=True)
    print(f"HSharp directories ensured at {HSHARP_DIR}.")
    if not os.path.exists(ICON_PATH):
        # Create a placeholder icon
        with open(ICON_PATH, "wb") as f:
            f.write(b"")  # Replace with your actual PNG binary if needed
        print(f"Default icon saved to {ICON_PATH}.")

def add_registry_entries():
    try:
        # Register .hs file extension
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, ".hs")
        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, ".hs", 0, reg.KEY_WRITE) as key:
            reg.SetValue(key, "", reg.REG_SZ, "HSharpFile")

        # Register HSharpFile
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, "HSharpFile\\DefaultIcon")
        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, "HSharpFile\\DefaultIcon", 0, reg.KEY_WRITE) as key:
            reg.SetValue(key, "", reg.REG_SZ, ICON_PATH)

        reg.CreateKey(reg.HKEY_CLASSES_ROOT, "HSharpFile\\shell\\open\\command")
        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, "HSharpFile\\shell\\open\\command", 0, reg.KEY_WRITE) as key:
            command = f'python "{os.path.abspath(__file__)}" "%1"'
            reg.SetValue(key, "", reg.REG_SZ, command)

        print(".hs file extension registered with default icon.")
    except Exception as e:
        print(f"Failed to register .hs extension: {e}")

def add_environment_variables():
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, "Environment", 0, reg.KEY_WRITE) as key:
            current_path = reg.QueryValueEx(key, "Path")[0]
            if HSHARP_DIR not in current_path:
                new_path = f"{current_path};{HSHARP_DIR}"
                reg.SetValueEx(key, "Path", 0, reg.REG_SZ, new_path)
                print("HSharp directory added to PATH.")
    except Exception as e:
        print(f"Failed to update PATH: {e}")

def check_and_install_python():
    try:
        subprocess.run(["python", "--version"], check=True)
        print("Python is already installed.")
    except FileNotFoundError:
        print("Python is not installed. Downloading and installing...")
        # You can customize this part to download Python automatically if needed.
        subprocess.run(["winget", "install", "-e", "--id", "Python.Python.3.11"], check=True)
        print("Python installed successfully.")

def check_for_updates():
    try:
        response = requests.get(GITHUB_VERSION_URL)
        response.raise_for_status()
        github_version = response.text.strip()

        local_version_path = os.path.join(HSHARP_DIR, "version.txt")
        local_version = ""
        if os.path.exists(local_version_path):
            with open(local_version_path, "r") as f:
                local_version = f.read().strip()

        if github_version != local_version:
            print(f"Updating HSharp from version {local_version} to {github_version}.")
            # Download and replace files if needed
            shutil.copy(local_version_path, f"{local_version_path}.old")
            with open(local_version_path, "w") as f:
                f.write(github_version)
        else:
            print("HSharp is up-to-date.")
    except Exception as e:
        print(f"Error checking for updates: {e}")

def install_framework(framework):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", framework], check=True)
        print(f"Framework {framework} installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install framework {framework}: {e}")

def compile_to_exe(file_path, icon_path=None):
    try:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return
        icon_option = f"--icon={icon_path}" if icon_path else f"--icon={ICON_PATH}"
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--onefile", icon_option, file_path],
            check=True
        )
        print(f"Compiled {file_path} to .exe.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to compile {file_path} to .exe: {e}")

# Command-line arguments handling
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments provided.")
    elif sys.argv[1] == "install":
        create_hsharp_directory()
        add_registry_entries()
        add_environment_variables()
        check_and_install_python()
    elif sys.argv[1] == "hs":
        if sys.argv[2] == "install" and len(sys.argv) > 3:
            install_framework(sys.argv[3])
        elif sys.argv[2] == "compile" and len(sys.argv) > 3:
            file = sys.argv[3]
            icon = sys.argv[4] if len(sys.argv) > 4 else None
            compile_to_exe(file, icon)
        else:
            print("Invalid hs command.")
    elif sys.argv[1] == "update":
        check_for_updates()
    else:
        print("Unknown command.")
