#!/usr/bin/env python3
"""
Simple API test script to verify Blissful is working
Make sure Blissful.py is running before executing this script
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:5000'

def print_test(name, passed, details=''):
    """Print test result"""
    status = '✓ PASS' if passed else '✗ FAIL'
    color = '\033[92m' if passed else '\033[91m'
    end = '\033[0m'
    print(f"{color}{status}{end} - {name}")
    if details:
        print(f"       {details}")

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=5)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get('status') == 'healthy'
        )
        
        details = f"FFmpeg: {data.get('ffmpeg_available')}, yt-dlp: {data.get('ytdlp_available')}"
        print_test('Health Check', passed, details)
        return passed
    except Exception as e:
        print_test('Health Check', False, f'Error: {e}')
        return False

def test_get_config():
    """Test getting configuration"""
    try:
        response = requests.get(f'{BASE_URL}/api/config', timeout=5)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            'output_format' in data
        )
        
        print_test('Get Configuration', passed)
        return passed
    except Exception as e:
        print_test('Get Configuration', False, f'Error: {e}')
        return False

def test_save_config():
    """Test saving configuration"""
    try:
        test_config = {
            'lidarr_url': 'http://test:8686',
            'lidarr_api_key': 'test_key',
            'output_format': 'mp3',
            'quality': '320k'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/config',
            json=test_config,
            timeout=5
        )
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get('success') == True
        )
        
        print_test('Save Configuration', passed)
        return passed
    except Exception as e:
        print_test('Save Configuration', False, f'Error: {e}')
        return False

def test_supported_sources():
    """Test getting supported sources"""
    try:
        response = requests.get(f'{BASE_URL}/api/supported-sources', timeout=5)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            'sources' in data and
            len(data['sources']) > 0
        )
        
        details = f"{len(data.get('sources', []))} sources available"
        print_test('Supported Sources', passed, details)
        return passed
    except Exception as e:
        print_test('Supported Sources', False, f'Error: {e}')
        return False

def test_web_interface():
    """Test if web interface is accessible"""
    try:
        response = requests.get(f'{BASE_URL}/', timeout=5)
        
        passed = (
            response.status_code == 200 and
            'text/html' in response.headers.get('content-type', '')
        )
        
        print_test('Web Interface', passed)
        return passed
    except Exception as e:
        print_test('Web Interface', False, f'Error: {e}')
        return False

def test_userscript_endpoint():
    """Test if userscript is accessible"""
    try:
        response = requests.get(f'{BASE_URL}/userscript', timeout=5)
        
        passed = (
            response.status_code == 200 and
            'Blissful' in response.text
        )
        
        print_test('Userscript Endpoint', passed)
        return passed
    except Exception as e:
        print_test('Userscript Endpoint', False, f'Error: {e}')
        return False

def test_download_validation():
    """Test download endpoint validation (without actually downloading)"""
    try:
        # Test with missing fields
        response = requests.post(
            f'{BASE_URL}/api/download-track',
            json={'artist': 'Test'},  # Missing 'title'
            timeout=5
        )
        
        passed = (
            response.status_code == 400 and
            'Missing required field' in response.json().get('error', '')
        )
        
        print_test('Download Validation', passed, 'Correctly rejects invalid requests')
        return passed
    except Exception as e:
        print_test('Download Validation', False, f'Error: {e}')
        return False

def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("Blissful API Test Suite")
    print("="*60)
    print("\nMake sure Blissful.py is running before starting tests!\n")
    
    # Check if service is running
    try:
        requests.get(f'{BASE_URL}/api/health', timeout=2)
    except requests.exceptions.ConnectionError:
        print('\033[91m✗ ERROR\033[0m - Cannot connect to Blissful service')
        print(f'Make sure the service is running at {BASE_URL}')
        print('\nStart the service with: python Blissful.py')
        return 1
    except Exception as e:
        print(f'\033[91m✗ ERROR\033[0m - {e}')
        return 1
    
    print("Running tests...\n")
    
    results = [
        test_health_check(),
        test_web_interface(),
        test_get_config(),
        test_save_config(),
        test_supported_sources(),
        test_userscript_endpoint(),
        test_download_validation()
    ]
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f'\033[92m✓ ALL TESTS PASSED\033[0m ({passed}/{total})')
        print('\nBlissful API is working correctly! 🎵')
        print('\nNext steps:')
        print('1. Open http://localhost:5000 in your browser')
        print('2. Configure your Lidarr connection')
        print('3. Install the userscript from the web interface')
        return 0
    else:
        print(f'\033[91m✗ SOME TESTS FAILED\033[0m ({passed}/{total} passed)')
        print('\nCheck the errors above and fix any issues.')
        return 1

if __name__ == '__main__':
    sys.exit(main())
