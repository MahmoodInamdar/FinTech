"""
🚀 PRODUCTION DATAVIZ PRO LAUNCHER v2.0
Production-ready launcher with all fixes and enhancements
Compatible with all devices and Python environments
"""
import sys
import os

def main():
    print("🏆 DataViz Pro v2.2.1 - Final Production Release")
    print("="*60)
    print("✅ Advanced large dataset handling (>1M rows, >100MB)")
    print("✅ Intelligent data sampling & optimization")
    print("✅ Enhanced AI with comprehensive context")
    print("✅ Multi-format support (CSV, Excel)")
    print("✅ Auto-insights & data quality scoring")
    print("✅ Multi-language support (13 languages)")
    print("✅ Production-ready error handling")
    print("✅ Complete enterprise software - FINAL")
    print("="*60)
    
    try:
        # Import required modules
        import streamlit.web.cli as stcli
        
        print("🚀 Starting Production DataViz Pro...")
        print("🌐 URL: http://localhost:8502")
        print("🌍 Languages: English, हिंदी, తెలుగు, தமிழ், বাংলা, ગુજરાતી, मराठी, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, ଓଡ଼ିଆ, অসমীয়া, اردو")
        print("🎨 Themes: Modern Blue, Dark Mode, Indian Orange, Royal Purple")
        print("💬 AI Modes: Short, Concise, Detailed, Technical")
        print("📊 Features: Complex data support, Auto-insights, Advanced AI, Export")
        print("-" * 60)
        
        # Set streamlit config for different port
        os.environ['STREAMLIT_SERVER_PORT'] = '8502'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        # Run streamlit
        sys.argv = ['streamlit', 'run', 'streamlit_app.py', '--server.port=8502', '--browser.gatherUsageStats=false']
        stcli.main()
        
    except ImportError as e:
        print(f"❌ Missing module: {e}")
        print("🔧 Installing packages automatically...")
        
        # Auto-install packages
        import subprocess
        packages = ['streamlit', 'plotly', 'pandas', 'numpy', 'google-generativeai', 'seaborn', 'matplotlib']
        
        for pkg in packages:
            print(f"📦 Installing {pkg}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                print(f"⚠️ Failed to install {pkg} - will continue")
        
        print("🔄 Restarting application...")
        subprocess.run([sys.executable, __file__])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🆘 Manual Backup Instructions:")
        print("1. Install Python 3.8+ from python.org")
        print("2. Run: pip install streamlit plotly pandas google-generativeai")
        print("3. Run: streamlit run streamlit_app.py")
        print("4. Open: http://localhost:8501")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using DataViz Pro! Production ready for any device.")
    except Exception as e:
        print(f"\n⚠️ Unexpected error: {e}")
        print("Please report this issue for support.")