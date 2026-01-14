"""
Request System Manager for Blissful
Handles music request configuration, artist search, and adding artists
"""

import logging

logger = logging.getLogger(__name__)


class RequestManager:
    """Manages music request system functionality"""
    
    def __init__(self, config_manager, lidarr_client_class):
        self.config_manager = config_manager
        self.LidarrClient = lidarr_client_class
    
    def get_request_config(self):
        """
        Get request system configuration (which auth methods are enabled)
        
        Returns:
            dict: Request configuration with enabled auth methods
        """
        try:
            config = self.config_manager.get_config()
            
            return {
                'success': True,
                'enabled': config.get('enable_requests', False),
                'jellyfin': {
                    'enabled': config.get('enable_jellyfin', False),
                    'url': config.get('jellyfin_url', '')
                },
                'emby': {
                    'enabled': config.get('enable_emby', False),
                    'url': config.get('emby_url', '')
                },
                'plex': {
                    'enabled': config.get('enable_plex', False)
                }
            }
        except Exception as e:
            logger.error(f"Error getting request config: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_artists(self, search_term):
        """
        Search for artists via Lidarr API
        
        Args:
            search_term: Artist name to search for
            
        Returns:
            dict: Search results with artist data
        """
        try:
            if not search_term:
                return {
                    'success': False,
                    'error': 'Search term required'
                }
            
            # Get Lidarr configuration
            config = self.config_manager.get_config()
            lidarr_url = config.get('lidarr_url')
            lidarr_api_key = config.get('lidarr_api_key')
            
            if not lidarr_url or not lidarr_api_key:
                return {
                    'success': False,
                    'error': 'Lidarr not configured'
                }
            
            # Search via Lidarr
            lidarr_client = self.LidarrClient(url=lidarr_url, api_key=lidarr_api_key)
            results = lidarr_client.search_artist_lidarr(search_term)
            
            return {
                'success': True,
                'results': results,
                'total': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching artists: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_artist_request(self, artist_data, username='Anonymous', monitored=False):
        """
        Add an artist to Lidarr (unmonitored by default for requests)
        
        Args:
            artist_data: Artist information from search
            username: Username of person making request
            monitored: Whether to monitor the artist (default: False for requests)
            
        Returns:
            dict: Result of adding artist
        """
        try:
            if not artist_data:
                return {
                    'success': False,
                    'error': 'Artist data required'
                }
            
            # Get Lidarr configuration
            config = self.config_manager.get_config()
            lidarr_url = config.get('lidarr_url')
            lidarr_api_key = config.get('lidarr_api_key')
            
            if not lidarr_url or not lidarr_api_key:
                return {
                    'success': False,
                    'error': 'Lidarr not configured'
                }
            
            # Add to Lidarr
            lidarr_client = self.LidarrClient(url=lidarr_url, api_key=lidarr_api_key)
            result = lidarr_client.add_artist(artist_data, monitored=monitored, search_for_missing=False)
            
            if result['success']:
                logger.info(f"Artist requested by {username}: {result.get('artist_name')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding artist request: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
