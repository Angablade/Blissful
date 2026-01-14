#!/usr/bin/env python3
"""
Quick troubleshooting script for common Blissful issues
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_issue(name, check_func):
    """Helper to run a check and report results"""
    try:
        result, message = check_func()
        status = "✓ OK" if result else "✗ ISSUE"
        color = '\033[92m' if result else '\033[91m'
        print(f"{color}{status}\033[0m - {name}")
        if message:
            print(f"       {message}")
        return result
    except Exception as e:
        print(f"\033[91m✗ ERROR\033[0m - {name}: {e}")
        return False

def check_python():
    """Check Python version"""
    version = sys.version_info
    ok = version.major >= 3 and version.minor >= 8
    msg = f"Python {version.major}.{version.minor}.{version.micro}"
    if not ok:
        msg += " (Need 3.8+)"
    return ok, msg

def check_flask():
    """Check Flask"""
    try:
        import flask
        return True, f"Flask {flask.__version__}"
    except ImportError:
        return False, "Run: pip install flask"

def check_flask_cors():
    """Check flask-cors"""
    try:
        import flask_cors
        return True, "flask-cors installed"
    except ImportError:
        return False, "Run: pip install flask-cors"

def check_requests():
    """Check requests"""
    try:
        import requests
        return True, f"requests {requests.__version__}"
    except ImportError:
        return False, "Run: pip install requests"

def check_ytdlp():
    """Check yt-dlp"""
    try:
        import yt_dlp
        return True, f"yt-dlp {yt_dlp.version.__version__}"
    except ImportError:
        return False, "Run: pip install yt-dlp"
    except:
        return True, "yt-dlp installed (version unknown)"

def check_ffmpeg():
    """Check FFmpeg"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0].split('version')[1].split()[0]
            return True, f"FFmpeg {version}"
        return False, "FFmpeg command failed"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"
    except Exception as e:
        return False, str(e)

def check_blissful_py():
    """Check Blissful.py exists"""
    exists = Path('Blissful.py').exists()
    msg = "Main file found" if exists else "Missing Blissful.py"
    return exists, msg

def check_config_manager():
    """Check config_manager.py"""
    exists = Path('config_manager.py').exists()
    if not exists:
        return False, "Missing config_manager.py"
    
    try:
        from config_manager import ConfigManager
        return True, "Module loads correctly"
    except Exception as e:
        return False, f"Import error: {e}"

def check_lidarr_client():
    """Check lidarr_client.py"""
    exists = Path('lidarr_client.py').exists()
    if not exists:
        return False, "Missing lidarr_client.py"
    
    try:
        from lidarr_client import LidarrClient
        return True, "Module loads correctly"
    except Exception as e:
        return False, f"Import error: {e}"

def check_download_manager():
    """Check download_manager.py"""
    exists = Path('download_manager.py').exists()
    if not exists:
        return False, "Missing download_manager.py"
    
    try:
        from download_manager import DownloadManager
        return True, "Module loads correctly"
    except Exception as e:
        return False, f"Import error: {e}"

def check_audio_converter():
    """Check audio_converter.py"""
    exists = Path('audio_converter.py').exists()
    if not exists:
        return False, "Missing audio_converter.py"
    
    try:
        from audio_converter import AudioConverter
        return True, "Module loads correctly"
    except Exception as e:
        return False, f"Import error: {e}"

def check_templates():
    """Check templates directory"""
    template_file = Path('templates/index.html')
    exists = template_file.exists()
    msg = "Web interface template found" if exists else "Missing templates/index.html"
    return exists, msg

def check_static():
    """Check static files"""
    css = Path('static/style.css').exists()
    js = Path('static/lidarr-userscript.user.js').exists()
    
    if css and js:
        return True, "All static files present"
    elif not css:
        return False, "Missing static/style.css"
    else:
        return False, "Missing static/lidarr-userscript.user.js"

def check_downloads_dir():
    """Check downloads directory"""
    downloads = Path('downloads')
    temp = Path('downloads/temp')
    
    if not downloads.exists():
        return False, "Missing downloads/ directory"
    if not temp.exists():
        return False, "Missing downloads/temp/ directory"
    
    return True, "Download directories exist"

def main():
    print("\n" + "="*60)
    print("Blissful Troubleshooting Script")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python),
        ("Flask Package", check_flask),
        ("Flask-CORS Package", check_flask_cors),
        ("Requests Package", check_requests),
        ("yt-dlp Package", check_ytdlp),
        ("FFmpeg", check_ffmpeg),
        ("Blissful.py", check_blissful_py),
        ("config_manager.py", check_config_manager),
        ("lidarr_client.py", check_lidarr_client),
        ("download_manager.py", check_download_manager),
        ("audio_converter.py", check_audio_converter),
        ("Templates", check_templates),
        ("Static Files", check_static),
        ("Download Directories", check_downloads_dir),
    ]
    
    results = []
    for name, func in checks:
        results.append(check_issue(name, func))
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"\033[92m✓ ALL CHECKS PASSED\033[0m ({passed}/{total})")
        print("\nYour installation looks good!")
        print("Run: python Blissful.py")
    else:
        print(f"\033[91m✗ {total - passed} ISSUES FOUND\033[0m ({passed}/{total} passed)")
        print("\nFix the issues above, then run:")
        print("  python test_setup.py")
    
    print("="*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
