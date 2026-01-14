#!/usr/bin/env python3
"""
Blissful Setup and Testing Script
Tests all components before running the full service
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# Add parent directory to path so we can import from extend
sys.path.insert(0, str(Path(__file__).parent.parent))

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}! {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version_str} (Required: 3.8+)")
        return True
    else:
        print_error(f"Python {version_str} - Need Python 3.8 or higher")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print_header("Checking Python Dependencies")
    
    dependencies = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'requests': 'requests',
        'yt_dlp': 'yt-dlp'
    }
    
    all_installed = True
    
    for module, package in dependencies.items():
        try:
            importlib.import_module(module)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("\nTo install missing dependencies, run:")
        print_info("    pip install -r requirements.txt")
    
    return all_installed

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print_header("Checking FFmpeg")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            print_success(f"FFmpeg is installed: {version_line}")
            return True
        else:
            print_error("FFmpeg command failed")
            return False
            
    except FileNotFoundError:
        print_error("FFmpeg is NOT installed")
        print_warning("\nFFmpeg is required for audio conversion!")
        print_info("Install FFmpeg:")
        print_info("  Windows: Download from https://ffmpeg.org/download.html")
        print_info("  macOS:   brew install ffmpeg")
        print_info("  Linux:   sudo apt install ffmpeg")
        return False
    except Exception as e:
        print_error(f"Error checking FFmpeg: {e}")
        return False

def check_directories():
    """Check and create required directories"""
    print_header("Checking Directories")
    
    # Get the project root directory (parent of extend folder)
    project_root = Path(__file__).parent.parent
    
    required_dirs = [
        'downloads',
        'downloads/temp',
        'templates',
        'templates/tabs',
        'static',
        'static/js'
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        path = project_root / dir_path
        if path.exists():
            print_success(f"Directory exists: {dir_path}")
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print_success(f"Created directory: {dir_path}")
            except Exception as e:
                print_error(f"Failed to create {dir_path}: {e}")
                all_ok = False
    
    return all_ok

def check_files():
    """Check if all required files exist"""
    print_header("Checking Required Files")
    
    # Get the project root directory (parent of extend folder)
    project_root = Path(__file__).parent.parent
    
    required_files = [
        'Blissful.py',
        'extend/config_manager.py',
        'extend/lidarr_client.py',
        'extend/download_manager.py',
        'extend/audio_converter.py',
        'extend/source_manager.py',
        'requirements.txt',
        'templates/index_new.html',
        'static/style.css',
        'static/lidarr-userscript.user.js'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        path = project_root / file_path
        if path.exists():
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File MISSING: {file_path}")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test importing the main modules"""
    print_header("Testing Module Imports")
    
    modules = [
        ('extend.config_manager', 'ConfigManager'),
        ('extend.lidarr_client', 'LidarrClient'),
        ('extend.download_manager', 'DownloadManager'),
        ('extend.audio_converter', 'AudioConverter'),
        ('extend.source_manager', 'SourceManager')
    ]
    
    all_ok = True
    
    for module_name, class_name in modules:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print_success(f"Successfully imported {module_name}.{class_name}")
            else:
                print_error(f"Module {module_name} missing class {class_name}")
                all_ok = False
        except ImportError as e:
            print_error(f"Failed to import {module_name}: {e}")
            all_ok = False
        except Exception as e:
            print_error(f"Error importing {module_name}: {e}")
            all_ok = False
    
    return all_ok

def test_basic_functionality():
    """Test basic functionality of modules"""
    print_header("Testing Basic Functionality")
    
    all_ok = True
    
    # Test ConfigManager
    try:
        from extend.config_manager import ConfigManager
        config = ConfigManager('test_config.json')
        
        # Test with valid configuration data
        test_data = {
            'lidarr_url': 'http://test:8686',
            'lidarr_api_key': 'test_key_123',
            'output_format': 'mp3',
            'quality': '320k'
        }
        
        # Save config
        save_result = config.save_config(test_data)
        if not save_result:
            print_error("ConfigManager: Failed to save config")
            all_ok = False
        else:
            # Load and verify
            loaded = config.get_config()
            
            # Check if our values are present
            if (loaded.get('lidarr_url') == 'http://test:8686' and
                loaded.get('lidarr_api_key') == 'test_key_123' and
                loaded.get('output_format') == 'mp3'):
                print_success("ConfigManager: Save and load works")
            else:
                print_error("ConfigManager: Data mismatch")
                all_ok = False
        
        # Cleanup
        Path('test_config.json').unlink(missing_ok=True)
    except Exception as e:
        print_error(f"ConfigManager test failed: {e}")
        all_ok = False
    
    # Test AudioConverter
    try:
        from extend.audio_converter import AudioConverter
        converter = AudioConverter()
        
        if converter.check_ffmpeg():
            print_success("AudioConverter: FFmpeg check works")
        else:
            print_warning("AudioConverter: FFmpeg not detected (expected if not installed)")
        
        formats = converter.get_supported_formats()
        if 'mp3' in formats and 'flac' in formats:
            print_success("AudioConverter: Format list works")
        else:
            print_error("AudioConverter: Format list incorrect")
            all_ok = False
    except Exception as e:
        print_error(f"AudioConverter test failed: {e}")
        all_ok = False
    
    # Test DownloadManager
    try:
        from extend.download_manager import DownloadManager
        dm = DownloadManager()
        
        if dm.check_ytdlp():
            print_success("DownloadManager: yt-dlp check works")
        else:
            print_warning("DownloadManager: yt-dlp not detected (expected if not installed)")
        
        sources = dm.get_supported_sources()
        if len(sources) > 0:
            print_success("DownloadManager: Source list works")
        else:
            print_error("DownloadManager: Source list empty")
            all_ok = False
    except Exception as e:
        print_error(f"DownloadManager test failed: {e}")
        all_ok = False
    
    return all_ok

def check_lidarr_config():
    """Check if Lidarr is configured and reachable"""
    print_header("Checking Lidarr Configuration")
    
    try:
        from extend.config_manager import ConfigManager
        from extend.lidarr_client import LidarrClient
        
        config = ConfigManager()
        cfg = config.get_config()
        
        lidarr_url = cfg.get('lidarr_url', '')
        lidarr_api_key = cfg.get('lidarr_api_key', '')
        
        # Check if configured
        if not lidarr_url or not lidarr_api_key:
            print_warning("Lidarr not configured yet")
            print_info("You can configure Lidarr after starting the service:")
            print_info("  1. Start Blissful: python Blissful.py")
            print_info("  2. Open: http://localhost:5000")
            print_info("  3. Go to Lidarr tab")
            print_info("  4. Enter Lidarr URL and API Key")
            print_info("  5. Click 'Test Connection' then 'Save'")
            return True  # Not an error, just not configured yet
        
        # Check if reachable
        print_info(f"Checking connection to: {lidarr_url}")
        
        try:
            lidarr_client = LidarrClient(url=lidarr_url, api_key=lidarr_api_key)
            status = lidarr_client.test_connection()
            
            if status.get('success'):
                version = status.get('version', 'Unknown')
                print_success(f"✓ Connected to Lidarr {version}")
                print_success(f"  URL: {lidarr_url}")
                print_info("  API Key: " + ("*" * 32) + lidarr_api_key[-8:] if len(lidarr_api_key) > 8 else "***")
                return True
            else:
                error = status.get('error', 'Unknown error')
                print_error(f"✗ Cannot connect to Lidarr: {error}")
                print_warning("Please check:")
                print_info("  - Is Lidarr running?")
                print_info(f"  - Can you access {lidarr_url} in a browser?")
                print_info("  - Is the API key correct?")
                print_info("  - Check Lidarr Settings → General → Security")
                return False
                
        except Exception as e:
            print_error(f"✗ Error connecting to Lidarr: {e}")
            print_warning("Lidarr may not be accessible from this machine")
            return False
            
    except Exception as e:
        print_error(f"Error checking Lidarr config: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    all_passed = all(results.values())
    
    for test, passed in results.items():
        if passed:
            print_success(f"{test}")
        else:
            print_error(f"{test}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print_success("\n✓ All checks passed! Ready to start Blissful.")
        print_info("\nTo start the service, run:")
        print_info("    python Blissful.py")
        print_info("\nThen open: http://localhost:5000")
        return True
    else:
        print_error("\n✗ Some checks failed. Please fix the issues above.")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}Blissful Setup and Testing Script{Colors.END}")
    print("This script will verify your installation is ready to run.\n")
    
    results = {
        "Python Version": check_python_version(),
        "Python Dependencies": check_dependencies(),
        "FFmpeg": check_ffmpeg(),
        "Directories": check_directories(),
        "Required Files": check_files(),
        "Module Imports": test_imports(),
        "Basic Functionality": test_basic_functionality(),
        "Lidarr Configuration": check_lidarr_config()
    }
    
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
