"""
Track Download Manager for Blissful
Handles individual track downloads with Lidarr integration
"""

import logging
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class TrackManager:
    """Manages track download operations"""
    
    def __init__(self, config_manager, lidarr_client_class, download_manager, audio_converter):
        self.config_manager = config_manager
        self.LidarrClient = lidarr_client_class
        self.download_manager = download_manager
        self.audio_converter = audio_converter
    
    def download_track(self, artist, title, album='', album_id=None, track_number=1):
        """
        Download a track based on metadata
        
        Args:
            artist: Artist name
            title: Track title
            album: Album name (optional)
            album_id: Lidarr album ID for organization (optional)
            track_number: Track number for filename (default: 1)
            
        Returns:
            dict: Download result with file path and rescan status
        """
        try:
            logger.info(f"Downloading track: {artist} - {title}")
            
            config = self.config_manager.get_config()
            
            # Search and download track
            download_result = self.download_manager.download_track(
                artist=artist,
                title=title,
                album=album,
                output_format=config.get('output_format', 'mp3'),
                source_priorities=config.get('source_priorities', [])
            )
            
            if not download_result['success']:
                return download_result
            
            # Convert to desired format
            output_format = config.get('output_format', 'mp3')
            converted_file = self.audio_converter.convert(
                input_file=download_result['file_path'],
                output_format=output_format,
                quality=config.get('quality', '320k')
            )
            
            # Organize file if album_id is provided
            final_path = converted_file
            if album_id and config.get('lidarr_url') and config.get('lidarr_api_key'):
                final_path = self._organize_track_file(
                    converted_file, 
                    album_id, 
                    title, 
                    album, 
                    track_number, 
                    output_format
                )
            
            # Trigger Lidarr rescan
            rescan_triggered = False
            if album_id and config.get('lidarr_url') and config.get('lidarr_api_key'):
                rescan_triggered = self._trigger_lidarr_rescan(album_id)
            
            return {
                'success': True,
                'message': 'Track downloaded and converted successfully',
                'file_path': final_path,
                'rescan_triggered': rescan_triggered,
                'album_id': album_id
            }
            
        except Exception as e:
            logger.error(f"Error downloading track: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _organize_track_file(self, converted_file, album_id, title, album, track_number, output_format):
        """
        Organize track file into Lidarr directory structure
        
        Args:
            converted_file: Path to converted audio file
            album_id: Lidarr album ID
            title: Track title
            album: Album name
            track_number: Track number
            output_format: Audio format extension
            
        Returns:
            str: Final file path
        """
        try:
            config = self.config_manager.get_config()
            
            # Get album details from Lidarr
            lidarr_client = self.LidarrClient(
                url=config.get('lidarr_url'),
                api_key=config.get('lidarr_api_key')
            )
            
            album_data = lidarr_client.get_album(int(album_id))
            if not album_data:
                logger.warning(f"Album {album_id} not found in Lidarr, keeping file in downloads")
                return converted_file
            
            # Get artist path and album title
            artist_path = album_data.get('artist', {}).get('path', '')
            album_title = album_data.get('title', album)
            
            if not artist_path:
                logger.warning("No artist path found, keeping file in downloads")
                return converted_file
            
            # Normalize artist path to use forward slashes
            artist_path = artist_path.replace('\\', '/')
            
            # Build target path with forward slashes
            safe_album = self.download_manager._sanitize_filename(album_title)
            safe_title = self.download_manager._sanitize_filename(title)
            track_num_str = str(track_number).zfill(2)
            filename = f"{track_num_str} - {safe_title}.{output_format}"
            
            # Construct path using forward slashes
            target_path = f"{artist_path}/{safe_album}/{filename}"
            
            logger.info(f"Target path (before mapping): {target_path}")
            
            # Move file to target location with path mapping
            if config.get('lidarr_path_mapping'):
                final_path = self.download_manager.move_to_target(
                    source_file=converted_file,
                    target_path=target_path,
                    path_mapping=config.get('lidarr_path_mapping')
                )
            else:
                # Direct move (no path mapping) - use Path for platform compatibility
                target = Path(target_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(converted_file, str(target))
                final_path = str(target)
                logger.info(f"Moved file to: {final_path}")
            
            return final_path
            
        except Exception as e:
            logger.warning(f"Failed to organize file to Lidarr path: {e}", exc_info=True)
            return converted_file
    
    def _trigger_lidarr_rescan(self, album_id):
        """
        Trigger Lidarr to rescan an album
        
        Args:
            album_id: Lidarr album ID
            
        Returns:
            bool: True if rescan triggered successfully
        """
        try:
            config = self.config_manager.get_config()
            
            lidarr_client = self.LidarrClient(
                url=config.get('lidarr_url'),
                api_key=config.get('lidarr_api_key')
            )
            
            rescan_triggered = lidarr_client.rescan_album(int(album_id))
            
            if rescan_triggered:
                logger.info(f"✅ Triggered Lidarr rescan for album {album_id}")
            else:
                logger.warning(f"⚠️ Failed to trigger Lidarr rescan for album {album_id}")
            
            return rescan_triggered
            
        except Exception as e:
            logger.warning(f"Failed to trigger Lidarr rescan: {e}")
            return False
