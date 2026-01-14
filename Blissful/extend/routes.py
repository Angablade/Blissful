"""
API Routes for Blissful
Defines all Flask routes and integrates with manager classes
"""

from flask import request, jsonify, render_template, Response
import logging

logger = logging.getLogger(__name__)


def register_routes(app, config_manager, lidarr_client, download_manager, 
                    audio_converter, source_manager, auth_manager, 
                    request_manager, album_manager, track_manager, 
                    sources_api, system_utils):
    """
    Register all API routes with the Flask app
    
    Args:
        app: Flask application instance
        config_manager: Configuration manager
        lidarr_client: Lidarr client class
        download_manager: Download manager
        audio_converter: Audio converter
        source_manager: Source manager
        auth_manager: Authentication manager
        request_manager: Request manager
        album_manager: Album manager
        track_manager: Track download manager
        sources_api: Sources API manager
        system_utils: System utilities
    """
    
    # ==================== PAGE ROUTES ====================
    
    @app.route('/')
    def index():
        """Serve the configuration web interface"""
        return render_template('index.html')
    
    @app.route('/request')
    def request_page():
        """Serve the music request page"""
        return render_template('request.html')
    
    # ==================== HEALTH & CONFIG ====================
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'ffmpeg_available': audio_converter.check_ffmpeg(),
            'ytdlp_available': download_manager.check_ytdlp()
        })
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration"""
        config = config_manager.get_config()
        safe_config = config.copy()
        if 'lidarr_api_key' in safe_config and safe_config['lidarr_api_key']:
            safe_config['lidarr_api_key'] = '***MASKED***'
        if 'jellyfin_api_key' in safe_config and safe_config['jellyfin_api_key']:
            safe_config['jellyfin_api_key'] = '***MASKED***'
        if 'emby_api_key' in safe_config and safe_config['emby_api_key']:
            safe_config['emby_api_key'] = '***MASKED***'
        return jsonify(safe_config)
    
    @app.route('/api/config', methods=['POST'])
    def save_config():
        """Save configuration"""
        try:
            data = request.json
            config_manager.save_config(data)
            return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== AUTHENTICATION ROUTES ====================
    
    @app.route('/api/auth/jellyfin', methods=['POST'])
    def auth_jellyfin():
        """Authenticate with Jellyfin"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        result = auth_manager.authenticate_jellyfin(username, password)
        status_code = result.pop('status_code', 200)
        return jsonify(result), status_code
    
    @app.route('/api/auth/emby', methods=['POST'])
    def auth_emby():
        """Authenticate with Emby"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        result = auth_manager.authenticate_emby(username, password)
        status_code = result.pop('status_code', 200)
        return jsonify(result), status_code
    
    @app.route('/api/auth/plex', methods=['POST'])
    def auth_plex():
        """Authenticate with Plex"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        result = auth_manager.authenticate_plex(username, password)
        status_code = result.pop('status_code', 200)
        return jsonify(result), status_code
    
    # ==================== REQUEST SYSTEM ROUTES ====================
    
    @app.route('/api/request/config', methods=['GET'])
    def get_request_config():
        """Get request system configuration"""
        return jsonify(request_manager.get_request_config())
    
    @app.route('/api/request/search', methods=['POST'])
    def search_artists_for_request():
        """Search for artists via Lidarr API"""
        data = request.json
        term = data.get('term', '')
        result = request_manager.search_artists(term)
        return jsonify(result)
    
    @app.route('/api/request/add', methods=['POST'])
    def add_artist_request():
        """Add an artist to Lidarr"""
        data = request.json
        artist_data = data.get('artist')
        monitored = data.get('monitored', False)
        username = data.get('username', 'Anonymous')
        
        result = request_manager.add_artist_request(artist_data, username, monitored)
        return jsonify(result)
    
    # ==================== ALBUM ROUTES ====================
    
    @app.route('/api/album-info/<album_id>', methods=['GET'])
    def get_album_info(album_id):
        """Fetch album information from Lidarr API"""
        result = album_manager.get_album_info(album_id)
        if not result['success']:
            return jsonify(result), 404 if 'not found' in result.get('error', '') else 400
        return jsonify(result)
    
    @app.route('/api/album-tracks/<album_id>', methods=['GET'])
    def get_album_tracks(album_id):
        """Fetch album tracks with their file status"""
        result = album_manager.get_album_tracks(album_id)
        if not result['success']:
            return jsonify(result), 404 if 'not found' in result.get('error', '') else 400
        return jsonify(result)
    
    @app.route('/api/download-album', methods=['POST'])
    def download_album():
        """Download all tracks in an album"""
        data = request.json
        
        required_fields = ['artist', 'album', 'tracks']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        result = album_manager.download_album(
            artist=data.get('artist'),
            album=data.get('album'),
            tracks=data.get('tracks', []),
            target_path=data.get('target_path', '')
        )
        return jsonify(result)
    
    # ==================== TRACK DOWNLOAD ROUTE ====================
    
    @app.route('/api/download-track', methods=['POST'])
    def download_track():
        """Download a track based on metadata"""
        data = request.json
        
        # Validate required fields
        required_fields = ['artist', 'title']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        result = track_manager.download_track(
            artist=data.get('artist'),
            title=data.get('title'),
            album=data.get('album', ''),
            album_id=data.get('album_id'),
            track_number=data.get('track_number', 1)
        )
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result)
    
    # ==================== LIDARR ROUTES ====================
    
    @app.route('/api/test-lidarr', methods=['POST'])
    def test_lidarr_connection():
        """Test Lidarr connection"""
        try:
            data = request.json
            lidarr = lidarr_client(
                url=data.get('lidarr_url'),
                api_key=data.get('lidarr_api_key')
            )
            status = lidarr.test_connection()
            return jsonify(status)
        except Exception as e:
            logger.error(f"Error testing Lidarr connection: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/get-api-key', methods=['POST'])
    def get_api_key():
        """Get the actual API key for testing (not masked)"""
        try:
            config = config_manager.get_config()
            api_key = config.get('lidarr_api_key', '')
            
            if api_key:
                return jsonify({'success': True, 'api_key': api_key})
            else:
                return jsonify({'success': False, 'error': 'No API key configured'})
        except Exception as e:
            logger.error(f"Error getting API key: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/lidarr-paths', methods=['POST'])
    def get_lidarr_paths():
        """Get root folders from Lidarr for path mapping"""
        try:
            data = request.json
            lidarr = lidarr_client(
                url=data.get('lidarr_url'),
                api_key=data.get('lidarr_api_key')
            )
            
            status = lidarr.test_connection()
            if not status.get('success'):
                return jsonify(status), 400
            
            paths = lidarr.get_root_folders()
            
            if paths:
                return jsonify({
                    'success': True,
                    'paths': paths
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No root folders found in Lidarr'
                })
                
        except Exception as e:
            logger.error(f"Error getting Lidarr paths: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== SOURCES ROUTES ====================
    
    @app.route('/api/supported-sources', methods=['GET'])
    def get_supported_sources():
        """Get list of supported download sources from yt-dlp"""
        category = request.args.get('category', None)
        tier = request.args.get('tier', None)
        search_query = request.args.get('q', None)
        music_only = request.args.get('music_only', 'false').lower() == 'true'
        
        result = sources_api.get_supported_sources(category, tier, search_query, music_only)
        return jsonify(result)
    
    @app.route('/api/sources/search', methods=['GET'])
    def search_sources():
        """Search for specific sources"""
        query = request.args.get('q', '')
        result = sources_api.search_sources(query)
        if not result['success']:
            return jsonify(result), 400
        return jsonify(result)
    
    @app.route('/api/sources/stats', methods=['GET'])
    def get_source_stats():
        """Get statistics about available sources"""
        return jsonify(sources_api.get_source_stats())
    
    @app.route('/api/sources/categories', methods=['GET'])
    def get_source_categories():
        """Get available source categories"""
        return jsonify(sources_api.get_source_categories())
    
    # ==================== SYSTEM UTILITIES ====================
    
    @app.route('/api/ytdlp/version', methods=['GET'])
    def get_ytdlp_version():
        """Get current yt-dlp version"""
        return jsonify(system_utils.get_ytdlp_version())
    
    @app.route('/api/ytdlp/upgrade', methods=['POST'])
    def upgrade_ytdlp():
        """Upgrade yt-dlp to latest version"""
        result = system_utils.upgrade_ytdlp()
        if not result['success']:
            return jsonify(result), 500
        return jsonify(result)
    
    @app.route('/api/system/info', methods=['GET'])
    def get_system_info():
        """Get system information"""
        return jsonify(system_utils.get_system_info())
    
    @app.route('/userscript')
    def serve_userscript():
        """Serve the userscript file with customized server URL and Lidarr URL"""
        server_url = request.host_url.rstrip('/')
        script_content, error = system_utils.generate_userscript(server_url)
        
        if error:
            return jsonify({'error': 'Failed to load userscript'}), 500
        
        response = Response(
            script_content,
            mimetype='text/javascript',
            headers={
                'Content-Disposition': 'attachment; filename="blissful-lidarr.user.js"',
                'Content-Type': 'text/javascript; charset=utf-8',
                'Cache-Control': 'no-cache'
            }
        )
        
        return response
    
    # ==================== DOCUMENTATION ROUTES ====================
    
    @app.route('/api/docs/<doc_name>', methods=['GET'])
    def get_documentation(doc_name):
        """Serve markdown documentation files"""
        import os
        
        # Sanitize filename
        safe_name = doc_name.replace('..', '').replace('/', '').replace('\\', '')
        
        # Try to read the markdown file
        docs_path = os.path.join('docs', f'{safe_name}.md')
        
        if not os.path.exists(docs_path):
            return jsonify({
                'success': False,
                'error': f'Documentation file not found: {safe_name}.md'
            }), 404
        
        try:
            with open(docs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return Response(
                content,
                mimetype='text/plain; charset=utf-8',
                headers={
                    'Cache-Control': 'public, max-age=300'  # Cache for 5 minutes
                }
            )
        except Exception as e:
            logger.error(f"Error reading documentation file {docs_path}: {e}")
            return jsonify({
                'success': False,
                'error': f'Error reading file: {str(e)}'
            }), 500
