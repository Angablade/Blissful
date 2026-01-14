"""
System Utilities for Blissful
Handles system info, yt-dlp updates, and userscript generation
"""

import logging
import os
import platform
import subprocess
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SystemUtils:
    """System utilities and tools"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def get_system_info(self):
        """
        Get system information (OS, Docker, Python version, etc.)
        
        Returns:
            dict: System information
        """
        try:
            # Detect if running in Docker
            is_docker = False
            try:
                with open('/proc/1/cgroup', 'r') as f:
                    is_docker = 'docker' in f.read()
            except:
                # Check for .dockerenv file (another Docker indicator)
                is_docker = os.path.exists('/.dockerenv')
            
            return {
                'success': True,
                'is_docker': is_docker,
                'os': platform.system(),
                'os_version': platform.version(),
                'python_version': platform.python_version(),
                'architecture': platform.machine()
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_ytdlp_version(self):
        """
        Get current and latest yt-dlp version
        
        Returns:
            dict: Version information and update status
        """
        try:
            # Get current yt-dlp version
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            current_version = result.stdout.strip() if result.returncode == 0 else 'Unknown'
            
            # Try to get latest version from GitHub API
            try:
                import requests
                response = requests.get(
                    'https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest',
                    timeout=3
                )
                if response.status_code == 200:
                    latest_version = response.json().get('tag_name', '').strip()
                else:
                    latest_version = 'Unknown'
            except:
                latest_version = 'Unknown'
            
            # Check if update is needed
            needs_update = False
            if current_version != 'Unknown' and latest_version != 'Unknown':
                # Simple version comparison (works for YYYY.MM.DD format)
                needs_update = current_version < latest_version
            
            return {
                'success': True,
                'current_version': current_version,
                'latest_version': latest_version,
                'needs_update': needs_update
            }
            
        except Exception as e:
            logger.error(f"Error getting yt-dlp version: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upgrade_ytdlp(self):
        """
        Upgrade yt-dlp to latest version
        
        Returns:
            dict: Upgrade result with new version
        """
        try:
            logger.info("Starting yt-dlp upgrade...")
            
            # Run pip upgrade
            result = subprocess.run(
                ['pip', 'install', '--upgrade', '--force-reinstall', 'yt-dlp'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("yt-dlp upgrade successful")
                
                # Get new version
                version_result = subprocess.run(
                    ['yt-dlp', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                new_version = version_result.stdout.strip()
                
                return {
                    'success': True,
                    'message': f'Successfully upgraded to yt-dlp {new_version}',
                    'new_version': new_version,
                    'output': result.stdout
                }
            else:
                logger.error(f"yt-dlp upgrade failed: {result.stderr}")
                return {
                    'success': False,
                    'error': 'Upgrade failed',
                    'output': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Upgrade timed out (>60s)'
            }
        except Exception as e:
            logger.error(f"Error upgrading yt-dlp: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_userscript(self, server_url):
        """
        Generate userscript with customized server URL and Lidarr URL
        
        Args:
            server_url: Base URL of the Blissful server
            
        Returns:
            tuple: (script_content, error_message)
        """
        try:
            config = self.config_manager.get_config()
            lidarr_url = config.get('lidarr_url', '')
            
            logger.info(f"Generating userscript with Lidarr URL: {lidarr_url}")
            logger.info(f"Microservice URL: {server_url}")
            
            # Read userscript template
            with open('static/lidarr-userscript.user.js', 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Generate @match patterns based on Lidarr URL
            if lidarr_url:
                try:
                    parsed = urlparse(lidarr_url)
                    lidarr_host = parsed.netloc or 'localhost:8686'
                    lidarr_scheme = parsed.scheme or 'http'
                    
                    logger.info(f"Parsed Lidarr - Host: {lidarr_host}, Scheme: {lidarr_scheme}")
                    
                    # Create specific match patterns for configured Lidarr
                    match_patterns = f"""// @match        {lidarr_scheme}://{lidarr_host}/*"""
                    
                    # Also add alternate scheme
                    alt_scheme = 'https' if lidarr_scheme == 'http' else 'http'
                    match_patterns += f"""
// @match        {alt_scheme}://{lidarr_host}/*"""
                    
                    logger.info(f"Generated match patterns:\n{match_patterns}")
                    
                except Exception as e:
                    logger.warning(f"Could not parse Lidarr URL: {e}")
                    # Fallback to localhost patterns
                    match_patterns = """// @match        http://localhost:8686/*
// @match        https://localhost:8686/*
// @match        http://127.0.0.1:8686/*
// @match        https://127.0.0.1:8686/*"""
            else:
                # No Lidarr URL configured, use localhost defaults
                logger.warning("No Lidarr URL configured, using localhost defaults")
                match_patterns = """// @match        http://localhost:8686/*
// @match        https://localhost:8686/*
// @match        http://127.0.0.1:8686/*
// @match        https://127.0.0.1:8686/*"""
            
            # Replace match patterns in script
            old_patterns = """// @match        http://localhost:8686/*
// @match        https://localhost:8686/*
// @match        http://127.0.0.1:8686/*
// @match        https://127.0.0.1:8686/*"""
            
            script_content = script_content.replace(old_patterns, match_patterns)
            
            # Replace microservice URL
            script_content = script_content.replace(
                "microserviceUrl: 'http://localhost:5000'",
                f"microserviceUrl: '{server_url}'"
            )
            
            logger.info("Userscript generated successfully")
            
            return (script_content, None)
            
        except Exception as e:
            logger.error(f"Error generating userscript: {e}", exc_info=True)
            return (None, str(e))
