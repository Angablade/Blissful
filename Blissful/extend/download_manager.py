import yt_dlp
import os
import logging
import shutil
from pathlib import Path
from typing import Dict, Optional
import subprocess

logger = logging.getLogger(__name__)

class DownloadManager:
    """Manager for downloading tracks using yt-dlp"""
    
    def __init__(self, download_dir: str = 'downloads'):
        """
        Initialize download manager
        
        Args:
            download_dir: Directory to store downloaded files
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Temporary directory for downloads
        self.temp_dir = self.download_dir / 'temp'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def check_ytdlp(self) -> bool:
        """
        Check if yt-dlp is available
        
        Returns:
            True if yt-dlp is available
        """
        try:
            import yt_dlp
            return True
        except ImportError:
            return False
    
    def download_track(
        self,
        artist: str,
        title: str,
        album: str = '',
        output_format: str = 'mp3',
        source_priorities: list = None
    ) -> Dict:
        """
        Download a track based on metadata
        
        Args:
            artist: Artist name
            title: Track title
            album: Album name (optional)
            output_format: Desired output format
            source_priorities: Optional list of source priorities
            
        Returns:
            Dict with success status and file path or error
        """
        try:
            # Construct search query
            search_query = f"{artist} - {title}"
            if album:
                search_query = f"{artist} - {album} - {title}"
            
            logger.info(f"Searching for: {search_query}")
            
            # Build source list based on priorities
            if source_priorities:
                sources = self._build_source_list(search_query, source_priorities)
            else:
                # Default fallback sources
                sources = [
                    f"ytsearch1:{search_query}",  # YouTube search
                    f"scsearch1:{search_query}",  # SoundCloud search
                ]
            
            downloaded_file = None
            last_error = None
            
            for source in sources:
                try:
                    logger.info(f"Trying source: {source}")
                    result = self._download_from_source(source, artist, title)
                    
                    if result['success']:
                        downloaded_file = result['file_path']
                        break
                    else:
                        last_error = result.get('error')
                        
                except Exception as e:
                    logger.warning(f"Failed to download from source {source}: {e}")
                    last_error = str(e)
                    continue
            
            if downloaded_file:
                return {
                    'success': True,
                    'file_path': downloaded_file,
                    'artist': artist,
                    'title': title
                }
            else:
                return {
                    'success': False,
                    'error': last_error or 'Could not find track from any source'
                }
                
        except Exception as e:
            logger.error(f"Error downloading track: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_source_list(self, search_query: str, priorities: list) -> list:
        """
        Build ordered source list based on priorities
        
        Args:
            search_query: The search query string
            priorities: List of source priority dicts
            
        Returns:
            List of yt-dlp source strings
        """
        sources = []
        
        for priority in priorities:
            if not priority.get('enabled', True):
                continue
            
            name = priority.get('name', '').lower()
            search = priority.get('search', '').lower()
            
            # YouTube and YouTube Music
            if 'youtube' in name or 'youtube.com' in search:
                if 'music' in name or 'music.youtube' in search:
                    sources.append(f"ytsearch1:'{search_query}' site:music.youtube.com")
                else:
                    sources.append(f"ytsearch1:{search_query}")
            
            # SoundCloud
            elif 'soundcloud' in name or 'soundcloud.com' in search:
                sources.append(f"scsearch1:{search_query}")
            
            # Bandcamp
            elif 'bandcamp' in name or 'bandcamp.com' in search:
                sources.append(f"https://bandcamp.com/search?q={search_query.replace(' ', '+')}")
            
            # Spotify
            elif 'spotify' in name or 'spotify.com' in search:
                sources.append(f"spsearch:{search_query}")
                # Add YouTube fallback for Spotify
                sources.append(f"ytsearch1:{search_query} audio")
            
            # Apple Music
            elif 'apple' in name or 'apple.com' in search:
                # Apple Music extraction, then fallback to YouTube
                sources.append(f"ytsearch1:{search_query} apple music")
            
            # Deezer
            elif 'deezer' in name or 'deezer.com' in search:
                sources.append(f"dzsearch:{search_query}")
                sources.append(f"ytsearch1:{search_query} deezer")
            
            # Tidal
            elif 'tidal' in name or 'tidal.com' in search:
                sources.append(f"ytsearch1:{search_query} tidal")
            
            # Mixcloud
            elif 'mixcloud' in name or 'mixcloud.com' in search:
                sources.append(f"https://www.mixcloud.com/search/?q={search_query.replace(' ', '+')}")
            
            # Archive.org
            elif 'archive' in name or 'archive.org' in search:
                sources.append(f"https://archive.org/search.php?query={search_query.replace(' ', '+')}&and[]=mediatype:audio")
            
            # Jamendo
            elif 'jamendo' in name or 'jamendo.com' in search:
                sources.append(f"ytsearch1:{search_query} jamendo")
            
            # Free Music Archive
            elif 'freemusicarchive' in name or 'freemusicarchive.org' in search:
                sources.append(f"ytsearch1:{search_query} free music archive")
            
            # Audiomack
            elif 'audiomack' in name or 'audiomack.com' in search:
                sources.append(f"https://audiomack.com/search?q={search_query.replace(' ', '+')}")
            
            # Vimeo
            elif 'vimeo' in name or 'vimeo.com' in search:
                sources.append(f"https://vimeo.com/search?q={search_query.replace(' ', '+')}")
            
            # Dailymotion
            elif 'dailymotion' in name or 'dailymotion.com' in search:
                sources.append(f"https://www.dailymotion.com/search/{search_query.replace(' ', '+')}")
            
            # TikTok
            elif 'tiktok' in name or 'tiktok.com' in search:
                sources.append(f"ytsearch1:{search_query} tiktok")
            
            # Reverbnation
            elif 'reverbnation' in name or 'reverbnation.com' in search:
                sources.append(f"ytsearch1:{search_query} reverbnation")
        
        # If no sources were added, add default fallbacks
        if not sources:
            sources = [
                f"ytsearch1:{search_query}",
                f"scsearch1:{search_query}",
            ]
        
        return sources
    
    def _download_from_source(self, source: str, artist: str, title: str) -> Dict:
        """
        Download from a specific source
        
        Args:
            source: yt-dlp source string
            artist: Artist name
            title: Track title
            
        Returns:
            Dict with success status and file path
        """
        try:
            # Sanitize filename
            safe_filename = self._sanitize_filename(f"{artist} - {title}")
            output_template = str(self.temp_dir / f"{safe_filename}.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'noplaylist': True,
                # Removed max_downloads - it was causing "MaxDownloadsReached" error
                # because yt-dlp counts search + download as 2 downloads
            }
            
            # Special handling for Spotify
            if source.startswith('spsearch:') or 'spotify.com' in source:
                # Spotify support requires additional configuration
                ydl_opts.update({
                    'username': 'oauth',  # Use OAuth if configured
                    'extract_flat': False,
                })
                logger.info("Using Spotify extractor")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to verify
                try:
                    info = ydl.extract_info(source, download=False)
                except Exception as e:
                    # If Spotify fails, return error to try next source
                    if 'spsearch:' in source or 'spotify' in source:
                        logger.warning(f"Spotify extraction failed: {e}")
                        return {
                            'success': False,
                            'error': f'Spotify unavailable: {str(e)}'
                        }
                    raise
                
                if not info or ('entries' in info and not info['entries']):
                    return {
                        'success': False,
                        'error': 'No results found'
                    }
                
                # Download the first result
                info = ydl.extract_info(source, download=True)
                
                # Find the downloaded file
                if info and 'entries' in info:
                    info = info['entries'][0]
                
                # The file should be in temp_dir with .mp3 extension
                expected_file = self.temp_dir / f"{safe_filename}.mp3"
                
                if expected_file.exists():
                    logger.info(f"Successfully downloaded: {expected_file}")
                    return {
                        'success': True,
                        'file_path': str(expected_file)
                    }
                else:
                    # Try to find the file with any extension
                    for file in self.temp_dir.glob(f"{safe_filename}.*"):
                        logger.info(f"Found downloaded file: {file}")
                        return {
                            'success': True,
                            'file_path': str(file)
                        }
                    
                    return {
                        'success': False,
                        'error': 'Downloaded file not found'
                    }
                    
        except yt_dlp.utils.DownloadError as e:
            logger.warning(f"Download error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error downloading: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file system storage
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def move_to_target(
        self,
        source_file: str,
        target_path: str,
        path_mapping: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Move file to target location with path mapping
        
        Args:
            source_file: Source file path
            target_path: Target path from Lidarr
            path_mapping: Optional path mapping dict (microservice_path -> lidarr_path)
            
        Returns:
            Final file path
        """
        try:
            source = Path(source_file)
            
            # Normalize target path to use forward slashes (cross-platform)
            target_path = target_path.replace('\\', '/')
            
            # Apply path mapping if provided
            if path_mapping:
                for micro_path, lidarr_path in path_mapping.items():
                    # Normalize both paths for comparison
                    micro_path_norm = micro_path.replace('\\', '/')
                    lidarr_path_norm = lidarr_path.replace('\\', '/')
                    target_path_norm = target_path.replace('\\', '/')
                    
                    if target_path_norm.startswith(lidarr_path_norm):
                        # Replace Lidarr path with microservice path
                        target_path = target_path_norm.replace(lidarr_path_norm, micro_path_norm, 1)
                        logger.info(f"Path mapping applied: {lidarr_path_norm} -> {micro_path_norm}")
                        break
            
            # Convert to Path object (handles platform-specific separators)
            target = Path(target_path)
            
            # Create target directory if it doesn't exist
            target.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Moving file from {source} to {target}")
            
            # Move file
            shutil.move(str(source), str(target))
            
            logger.info(f"✅ Successfully moved file to: {target}")
            return str(target)
            
        except Exception as e:
            logger.error(f"❌ Error moving file to target: {e}", exc_info=True)
            # Return source path if move failed
            return source_file
    
    def cleanup_temp(self):
        """Clean up temporary download directory"""
        try:
            for file in self.temp_dir.glob('*'):
                if file.is_file():
                    file.unlink()
            logger.info("Cleaned up temporary downloads")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {e}")
    
    def get_supported_sources(self) -> list:
        """
        Get list of supported download sources
        
        Returns:
            List of supported source names
        """
        return [
            'YouTube',
            'YouTube Music',
            'SoundCloud',
            'Bandcamp',
            'Spotify (via youtube-dl extractor)',
            'And many more supported by yt-dlp'
        ]
