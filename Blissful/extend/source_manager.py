"""
YT-DLP Source Manager
Dynamically retrieves and manages all supported extractors from yt-dlp
"""

import logging
from typing import List, Dict, Optional
import yt_dlp

logger = logging.getLogger(__name__)

class SourceManager:
    """Manager for yt-dlp extractors and sources"""
    
    def __init__(self):
        """Initialize the source manager"""
        self._extractors_cache = None
        self._categories = {
            'music': ['youtube', 'soundcloud', 'bandcamp', 'spotify', 'deezer', 'tidal', 
                     'applemusic', 'mixcloud', 'audiomack', 'jamendo', 'reverbnation'],
            'video': ['youtube', 'vimeo', 'dailymotion', 'tiktok', 'twitch'],
            'podcast': ['spotify', 'soundcloud', 'mixcloud', 'youtube'],
            'archive': ['archive', 'internetarchive'],
            'free': ['jamendo', 'freemusicarchive', 'ccmixter', 'archive']
        }
    
    def get_all_extractors(self) -> List[Dict]:
        """
        Get all available yt-dlp extractors
        
        Returns:
            List of extractor information dictionaries
        """
        if self._extractors_cache is not None:
            return self._extractors_cache
        
        try:
            extractors = []
            
            # Get all extractor classes from yt-dlp
            from yt_dlp.extractor import _ALL_CLASSES
            
            for extractor_class in _ALL_CLASSES:
                try:
                    # Get extractor info
                    ie_key = getattr(extractor_class, 'IE_NAME', extractor_class.__name__)
                    ie_desc = getattr(extractor_class, 'IE_DESC', None) or getattr(extractor_class, '_VALID_URL', 'No description')
                    
                    # Determine if this is likely a music source
                    is_music = self._is_music_source(ie_key.lower())
                    
                    # Get category
                    category = self._categorize_source(ie_key.lower())
                    
                    # Determine tier based on popularity and reliability
                    tier = self._assign_tier(ie_key.lower())
                    
                    # Check if search is supported - check for _SEARCH_KEY or known search prefixes
                    search_supported = (
                        hasattr(extractor_class, '_SEARCH_KEY') or 
                        self._has_search_support(ie_key.lower())
                    )
                    
                    extractors.append({
                        'name': self._format_name(ie_key),
                        'ie_key': ie_key,
                        'description': ie_desc if isinstance(ie_desc, str) else str(ie_desc)[:100],
                        'is_music': is_music,
                        'category': category,
                        'tier': tier,
                        'search_supported': search_supported,
                        'enabled': True
                    })
                    
                except Exception as e:
                    logger.debug(f"Error processing extractor {extractor_class}: {e}")
                    continue
            
            # Sort by tier, then name
            extractors.sort(key=lambda x: (x['tier'], x['name']))
            
            self._extractors_cache = extractors
            logger.info(f"Loaded {len(extractors)} yt-dlp extractors")
            
            return extractors
            
        except Exception as e:
            logger.error(f"Error getting extractors: {e}", exc_info=True)
            return self._get_fallback_sources()
    
    def get_music_extractors(self) -> List[Dict]:
        """
        Get only music-focused extractors
        
        Returns:
            List of music extractor information
        """
        all_extractors = self.get_all_extractors()
        return [e for e in all_extractors if e['is_music']]
    
    def search_extractors(self, query: str) -> List[Dict]:
        """
        Search extractors by name or description
        
        Args:
            query: Search query
            
        Returns:
            List of matching extractors
        """
        query = query.lower()
        all_extractors = self.get_all_extractors()
        
        matches = []
        for extractor in all_extractors:
            if (query in extractor['name'].lower() or 
                query in extractor['description'].lower() or
                query in extractor['ie_key'].lower()):
                matches.append(extractor)
        
        return matches
    
    def get_extractor_by_name(self, name: str) -> Optional[Dict]:
        """
        Get specific extractor by name
        
        Args:
            name: Extractor name or IE_KEY
            
        Returns:
            Extractor info or None
        """
        all_extractors = self.get_all_extractors()
        name_lower = name.lower()
        
        for extractor in all_extractors:
            if (extractor['name'].lower() == name_lower or 
                extractor['ie_key'].lower() == name_lower):
                return extractor
        
        return None
    
    def get_search_prefix(self, extractor_name: str) -> Optional[str]:
        """
        Get the search prefix for an extractor
        
        Args:
            extractor_name: Name of the extractor
            
        Returns:
            Search prefix (e.g., 'ytsearch:', 'scsearch:') or None
        """
        extractor_name = extractor_name.lower()
        
        # Known search prefixes
        search_prefixes = {
            'youtube': 'ytsearch',
            'youtubemusic': 'ytsearch',
            'soundcloud': 'scsearch',
            'spotify': 'spsearch',
            'deezer': 'dzsearch',
        }
        
        for key, prefix in search_prefixes.items():
            if key in extractor_name:
                return f"{prefix}:"
        
        return None
    
    def _is_music_source(self, ie_key: str) -> bool:
        """Determine if extractor is music-focused"""
        music_keywords = [
            'music', 'sound', 'audio', 'song', 'track', 'album', 
            'spotify', 'deezer', 'tidal', 'bandcamp', 'jamendo',
            'mixcloud', 'audiomack', 'reverbnation'
        ]
        
        return any(keyword in ie_key for keyword in music_keywords)
    
    def _categorize_source(self, ie_key: str) -> str:
        """Categorize the source"""
        for category, keywords in self._categories.items():
            if any(keyword in ie_key for keyword in keywords):
                return category
        return 'other'
    
    def _assign_tier(self, ie_key: str) -> int:
        """
        Assign tier based on popularity and reliability
        
        Tier 1: Most popular, most reliable
        Tier 2: Popular, reliable
        Tier 3: Less common but functional
        Tier 4: Niche or experimental
        """
        tier1_sources = [
            'youtube', 'soundcloud', 'bandcamp', 'spotify', 'vimeo'
        ]
        
        tier2_sources = [
            'deezer', 'tidal', 'applemusic', 'mixcloud', 'archive',
            'dailymotion', 'tiktok', 'twitch'
        ]
        
        tier3_sources = [
            'jamendo', 'audiomack', 'reverbnation', 'freemusicarchive',
            'ccmixter', 'internet'
        ]
        
        if any(source in ie_key for source in tier1_sources):
            return 1
        elif any(source in ie_key for source in tier2_sources):
            return 2
        elif any(source in ie_key for source in tier3_sources):
            return 3
        else:
            return 4
    
    def _format_name(self, ie_key: str) -> str:
        """Format extractor name for display"""
        # Remove common suffixes
        name = ie_key.replace('IE', '').replace(':', '')
        
        # Capitalize properly
        if name.lower() == 'youtube':
            return 'YouTube'
        elif name.lower() == 'soundcloud':
            return 'SoundCloud'
        elif name.lower() == 'bandcamp':
            return 'Bandcamp'
        elif name.lower() == 'spotify':
            return 'Spotify'
        elif 'youtube' in name.lower() and 'music' in name.lower():
            return 'YouTube Music'
        else:
            # Title case
            return ' '.join(word.capitalize() for word in name.split('_'))
    
    def _get_fallback_sources(self) -> List[Dict]:
        """
        Get fallback source list if yt-dlp extraction fails
        
        Returns:
            Basic source list
        """
        return [
            {
                'name': 'YouTube Music',
                'ie_key': 'youtube',
                'description': 'Music videos and audio from YouTube',
                'is_music': True,
                'category': 'music',
                'tier': 1,
                'search_supported': True,
                'enabled': True
            },
            {
                'name': 'YouTube',
                'ie_key': 'youtube',
                'description': 'Video sharing platform',
                'is_music': False,
                'category': 'video',
                'tier': 1,
                'search_supported': True,
                'enabled': True
            },
            {
                'name': 'SoundCloud',
                'ie_key': 'soundcloud',
                'description': 'Music and audio platform',
                'is_music': True,
                'category': 'music',
                'tier': 1,
                'search_supported': True,
                'enabled': True
            },
            {
                'name': 'Bandcamp',
                'ie_key': 'bandcamp',
                'description': 'Independent music platform',
                'is_music': True,
                'category': 'music',
                'tier': 1,
                'search_supported': False,
                'enabled': True
            },
            {
                'name': 'Spotify',
                'ie_key': 'spotify',
                'description': 'Music streaming service',
                'is_music': True,
                'category': 'music',
                'tier': 1,
                'search_supported': True,
                'enabled': True
            }
        ]
    
    def get_stats(self) -> Dict:
        """
        Get statistics about available extractors
        
        Returns:
            Dictionary with stats
        """
        extractors = self.get_all_extractors()
        
        return {
            'total': len(extractors),
            'music': len([e for e in extractors if e['is_music']]),
            'search_supported': len([e for e in extractors if e['search_supported']]),
            'by_tier': {
                1: len([e for e in extractors if e['tier'] == 1]),
                2: len([e for e in extractors if e['tier'] == 2]),
                3: len([e for e in extractors if e['tier'] == 3]),
                4: len([e for e in extractors if e['tier'] == 4])
            },
            'by_category': {
                'music': len([e for e in extractors if e['category'] == 'music']),
                'video': len([e for e in extractors if e['category'] == 'video']),
                'podcast': len([e for e in extractors if e['category'] == 'podcast']),
                'archive': len([e for e in extractors if e['category'] == 'archive']),
                'free': len([e for e in extractors if e['category'] == 'free']),
                'other': len([e for e in extractors if e['category'] == 'other'])
            }
        }
    
    def _has_search_support(self, ie_key: str) -> bool:
        """
        Check if extractor has search support
        
        Args:
            ie_key: Extractor IE_KEY
            
        Returns:
            True if search is supported
        """
        # Known extractors with search support
        search_supported = [
            'youtube', 'soundcloud', 'spotify', 'deezer', 'tidal',
            'dailymotion', 'vimeo', 'bilibili', 'niconico',
            'mixcloud', 'bandcamp', 'applemusic', 'tiktok',
            'googlevideo', 'yandex', 'rutube'
        ]
        
        return any(keyword in ie_key for keyword in search_supported)
