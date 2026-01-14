"""
Sources API Manager for Blissful
Handles yt-dlp source discovery and management
"""

import logging

logger = logging.getLogger(__name__)


class SourcesAPI:
    """Manages download source information and queries"""
    
    def __init__(self, source_manager):
        self.source_manager = source_manager
    
    def get_supported_sources(self, category=None, tier=None, search_query=None, music_only=False):
        """
        Get list of supported download sources from yt-dlp
        
        Args:
            category: Filter by category (music, video, podcast, etc.)
            tier: Filter by tier (1, 2, 3, 4)
            search_query: Search for specific sources
            music_only: Only show music-focused sources
            
        Returns:
            dict: Sources list with stats
        """
        try:
            # Get extractors based on filters
            if search_query:
                sources = self.source_manager.search_extractors(search_query)
            elif music_only:
                sources = self.source_manager.get_music_extractors()
            else:
                sources = self.source_manager.get_all_extractors()
            
            # Apply additional filters
            if category:
                sources = [s for s in sources if s.get('category') == category]
            
            if tier:
                try:
                    tier_num = int(tier)
                    sources = [s for s in sources if s.get('tier') == tier_num]
                except ValueError:
                    logger.warning(f"Invalid tier value: {tier}")
            
            # Get stats
            stats = self.source_manager.get_stats()
            
            return {
                'success': True,
                'sources': sources,
                'total': len(sources),
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting supported sources: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'sources': []
            }
    
    def search_sources(self, query):
        """
        Search for specific sources by name or description
        
        Args:
            query: Search query string
            
        Returns:
            dict: Search results
        """
        try:
            if not query:
                return {
                    'success': False,
                    'error': 'Query parameter required'
                }
            
            results = self.source_manager.search_extractors(query)
            
            return {
                'success': True,
                'results': results,
                'total': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching sources: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_source_stats(self):
        """
        Get statistics about available sources
        
        Returns:
            dict: Source statistics
        """
        try:
            stats = self.source_manager.get_stats()
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            logger.error(f"Error getting source stats: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_source_categories(self):
        """
        Get available source categories
        
        Returns:
            dict: List of categories with descriptions
        """
        return {
            'success': True,
            'categories': [
                {
                    'id': 'music',
                    'name': 'Music Services',
                    'description': 'Dedicated music streaming platforms'
                },
                {
                    'id': 'video',
                    'name': 'Video Platforms',
                    'description': 'Video sites with music content'
                },
                {
                    'id': 'podcast',
                    'name': 'Podcast Services',
                    'description': 'Podcast and audio platforms'
                },
                {
                    'id': 'archive',
                    'name': 'Archives',
                    'description': 'Public domain and archival sites'
                },
                {
                    'id': 'free',
                    'name': 'Free Music',
                    'description': 'Creative Commons and free music platforms'
                },
                {
                    'id': 'other',
                    'name': 'Other',
                    'description': 'Miscellaneous sources'
                }
            ]
        }
