#!/usr/bin/env python3
"""
Startup script for Data Analytics AI Application
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv not installed, skip loading

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'openai',
        'numpy'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n🔧 Please install requirements:")
        print("   pip install -r requirements.txt")
        return False

    print("✅ All required packages are installed!")
    return True

def check_openai_api_key():
    """Check if OpenAI API key is available"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API Key not found in environment variables.")
        print("   You can enter it in the app interface or set OPENAI_API_KEY environment variable.")
        return False

    print("✅ OpenAI API Key found in environment!")
    return True

def run_streamlit(port=8501, host='localhost'):
    """Run the Streamlit application"""
    try:
        print(f"🚀 Starting Data Analytics AI Application...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   URL: http://{host}:{port}")
        print("\n   Press Ctrl+C to stop the application\n")

        # Run streamlit
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'main.py',
            '--server.port', str(port),
            '--server.address', host,
            '--theme.base', 'light'
        ]

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Data Analytics AI Application')
    parser.add_argument('--port', '-p', type=int, default=8501, help='Port to run the application on')
    parser.add_argument('--host', default='localhost', help='Host to bind the application to')
    parser.add_argument('--skip-checks', action='store_true', help='Skip dependency and API key checks')

    args = parser.parse_args()

    print("🔍 Data Analytics AI - Startup Script")
    print("=" * 50)

    if not args.skip_checks:
        # Check requirements
        if not check_requirements():
            sys.exit(1)

        # Check API key (warning only)
        check_openai_api_key()

        print("=" * 50)

    # Run the application
    run_streamlit(args.port, args.host)

if __name__ == "__main__":
    main()
