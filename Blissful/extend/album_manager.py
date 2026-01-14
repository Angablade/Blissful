"""
Album Management Module for Blissful
Handles album information, tracks, and bulk album downloads
"""

import logging

logger = logging.getLogger(__name__)


class AlbumManager:
    """Manages album-related operations"""
    
    def __init__(self, config_manager, lidarr_client_class, download_manager, audio_converter):
        self.config_manager = config_manager
        self.LidarrClient = lidarr_client_class
        self.download_manager = download_manager
        self.audio_converter = audio_converter
    
    def get_album_info(self, album_id):
        """
        Fetch album information from Lidarr API
        
        Args:
            album_id: The foreign album ID (GUID) from Lidarr URL
            
        Returns:
            dict: Album information including title, artist, path
        """
        try:
            # Get Lidarr configuration
            config = self.config_manager.get_config()
            lidarr_url = config.get('lidarr_url')
            lidarr_api_key = config.get('lidarr_api_key')
            
            if not lidarr_url or not lidarr_api_key:
                return {
                    'success': False,
                    'error': 'Lidarr not configured'
                }
            
            # Create Lidarr client
            lidarr_client = self.LidarrClient(url=lidarr_url, api_key=lidarr_api_key)
            
            # Fetch album data
            album_data = lidarr_client.get_album_by_foreign_id(album_id)
            
            if not album_data:
                return {
                    'success': False,
                    'error': f'Album not found: {album_id}'
                }
            
            # Extract relevant information
            result = {
                'success': True,
                'title': album_data.get('title', 'Unknown Album'),
                'artist': album_data.get('artist', {}).get('artistName', 'Unknown Artist'),
                'foreignAlbumId': album_data.get('foreignAlbumId'),
                'lidarrAlbumId': album_data.get('id'),
                'path': album_data.get('artist', {}).get('path', ''),
                'releaseDate': album_data.get('releaseDate'),
                'trackCount': album_data.get('statistics', {}).get('trackCount', 0)
            }
            
            logger.info(f"Fetched album info: {result['artist']} - {result['title']} (Path: {result['path']})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching album info for {album_id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_album_tracks(self, album_id):
        """
        Fetch album tracks with their file status from Lidarr
        
        Args:
            album_id: The Lidarr album ID (numeric)
            
        Returns:
            dict: Track list with file status
        """
        try:
            # Get Lidarr configuration
            config = self.config_manager.get_config()
            lidarr_url = config.get('lidarr_url')
            lidarr_api_key = config.get('lidarr_api_key')
            
            if not lidarr_url or not lidarr_api_key:
                return {
                    'success': False,
                    'error': 'Lidarr not configured'
                }
            
            # Create Lidarr client
            lidarr_client = self.LidarrClient(url=lidarr_url, api_key=lidarr_api_key)
            
            # Fetch tracks
            tracks = lidarr_client.get_album_tracks(int(album_id))
            
            if not tracks:
                return {
                    'success': False,
                    'error': f'No tracks found for album {album_id}'
                }
            
            # Format track data
            track_list = []
            for track in tracks:
                track_list.append({
                    'id': track.get('id'),
                    'trackNumber': track.get('trackNumber'),
                    'title': track.get('title'),
                    'duration': track.get('duration', 0),
                    'hasFile': track.get('hasFile', False),
                    'trackFileId': track.get('trackFileId'),
                })
            
            logger.info(f"Fetched {len(track_list)} tracks for album {album_id}")
            
            return {
                'success': True,
                'tracks': track_list,
                'total': len(track_list)
            }
            
        except Exception as e:
            logger.error(f"Error fetching tracks for album {album_id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_album(self, artist, album, tracks, target_path=''):
        """
        Download all tracks in an album
        
        Args:
            artist: Artist name
            album: Album name
            tracks: List of track objects with title and optional target_path
            target_path: Target directory path
            
        Returns:
            dict: Download results for all tracks
        """
        try:
            logger.info(f"Downloading album: {artist} - {album} ({len(tracks)} tracks)")
            
            results = {
                'success': True,
                'album': album,
                'artist': artist,
                'total_tracks': len(tracks),
                'successful': 0,
                'failed': 0,
                'tracks': []
            }
            
            config = self.config_manager.get_config()
            
            for track in tracks:
                track_result = {
                    'title': track.get('title'),
                    'success': False,
                    'error': None
                }
                
                try:
                    # Download track
                    download_result = self.download_manager.download_track(
                        artist=artist,
                        title=track.get('title'),
                        album=album,
                        output_format=config.get('output_format', 'mp3'),
                        source_priorities=config.get('source_priorities', [])
                    )
                    
                    if download_result['success']:
                        # Convert track
                        converted_file = self.audio_converter.convert(
                            input_file=download_result['file_path'],
                            output_format=config.get('output_format', 'mp3'),
                            quality=config.get('quality', '320k')
                        )
                        
                        # Move to target if specified
                        if target_path and config.get('lidarr_path_mapping'):
                            final_path = self.download_manager.move_to_target(
                                source_file=converted_file,
                                target_path=track.get('target_path', target_path),
                                path_mapping=config.get('lidarr_path_mapping')
                            )
                            track_result['file_path'] = final_path
                        else:
                            track_result['file_path'] = converted_file
                        
                        track_result['success'] = True
                        results['successful'] += 1
                    else:
                        track_result['error'] = download_result.get('error')
                        results['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Error downloading track {track.get('title')}: {e}")
                    track_result['error'] = str(e)
                    results['failed'] += 1
                
                results['tracks'].append(track_result)
            
            results['success'] = results['failed'] < results['total_tracks']
            
            return results
            
        except Exception as e:
            logger.error(f"Error downloading album: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
