#!/usr/bin/env python3
"""
Setup script for Python Terminal
"""

import sys
import subprocess
import os
from pathlib import Path

def install_package(package_name):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        'psutil',  # System monitoring
    ]
    
    optional_packages = [
        'colorama',  # Cross-platform colored terminal text (for Windows)
    ]
    
    print("🔍 Checking dependencies...")
    
    missing_required = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} - Missing")
    
    missing_optional = []
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK (optional)")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package} - Missing (optional)")
    
    # Install missing required packages
    if missing_required:
        print(f"\n📦 Installing required packages: {', '.join(missing_required)}")
        for package in missing_required:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                return False
    
    # Install missing optional packages (with user confirmation)
    if missing_optional:
        print(f"\n🔧 Optional packages available: {', '.join(missing_optional)}")
        install_optional = input("Install optional packages? (y/N): ").strip().lower()
        
        if install_optional in ['y', 'yes']:
            for package in missing_optional:
                print(f"Installing {package}...")
                if install_package(package):
                    print(f"✅ {package} installed successfully")
                else:
                    print(f"⚠️  Failed to install {package} (optional)")
    
    return True

def create_directory_structure():
    """Create necessary directory structure"""
    directories = [
        'commands',
        'filesystem', 
        'utils',
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        # Create __init__.py files for Python packages
        init_file = Path(directory) / '__init__.py'
        if not init_file.exists():
            init_file.touch()

def create_run_script():
    """Create a convenient run script"""
    if os.name == 'nt':  # Windows
        script_content = '''@echo off
python main.py %*
'''
        with open('run.bat', 'w') as f:
            f.write(script_content)
        print("✅ Created run.bat for Windows")
    else:  # Unix-like systems
        script_content = '''#!/bin/bash
python3 main.py "$@"
'''
        with open('run.sh', 'w') as f:
            f.write(script_content)
        os.chmod('run.sh', 0o755)
        print("✅ Created run.sh for Unix/Linux/macOS")

def main():
    """Main setup function"""
    print("🚀 Python Terminal Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Create directory structure
    print("\n📁 Creating directory structure...")
    create_directory_structure()
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("\n❌ Failed to install required dependencies")
        return False
    
    # Create run scripts
    print("\n📜 Creating run scripts...")
    create_run_script()
    
    print("\n🎉 Setup complete!")
    print("\nTo run the terminal:")
    if os.name == 'nt':
        print("  run.bat")
        print("  or: python main.py")
    else:
        print("  ./run.sh")
        print("  or: python3 main.py")
    
    print("\nOptions:")
    print("  --virtual    Use virtual filesystem (safe mode)")
    print("  --help       Show help message")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)