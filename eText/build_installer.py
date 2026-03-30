import os
import subprocess
import sys

def build_installer():
    # Change to the directory containing the installer configuration
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Build the installer using pynsist
    try:
        result = subprocess.run([
            sys.executable, '-m', 'nsist', 'installer.cfg'
        ], check=True, capture_output=True, text=True)

        print("Installer built successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building installer: {e}")
        print(f"stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    build_installer()