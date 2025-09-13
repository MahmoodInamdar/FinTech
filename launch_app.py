"""
🚀 SMART LAUNCHER - Finds available port automatically
"""
import subprocess
import sys
import socket

def find_free_port():
    """Find a free port starting from 8501"""
    for port in range(8501, 8510):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except:
            continue
    return 8599  # fallback port

def main():
    print("🏆 DataViz Pro v2.1 - Complete Indian Language Support")
    print("="*60)
    print("✅ File persistence across UI changes")
    print("✅ Controlled AI response lengths") 
    print("✅ Multi-language support (13 languages)")
    print("✅ Dynamic theming (4 themes)")
    print("✅ Data-focused AI analysis")
    print("✅ All compatibility issues fixed")
    print("="*60)
    
    # Find available port
    port = find_free_port()
    
    print(f"🚀 Starting Production DataViz Pro...")
    print(f"🌐 URL: http://localhost:{port}")
    print("🌍 Languages: English, हिंदी, తెలుగు, தமிழ், বাংলা, ગુજરાતી, मराठी, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, ଓଡ଼ିଆ, অসমীয়া, اردو")
    print("🎨 Themes: Modern Blue, Dark Mode, Indian Orange, Royal Purple")
    print("💬 AI Modes: Short, Concise, Detailed, Technical")
    print("📊 Features: Persistent files, Smart AI, Export data")
    print("-" * 60)
    
    try:
        # Run streamlit with auto-detected port
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            f'--server.port={port}',
            '--browser.gatherUsageStats=false'
        ])
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🆘 Manual solution:")
        print(f"Run: streamlit run streamlit_app.py --server.port={port}")

if __name__ == "__main__":
    main()