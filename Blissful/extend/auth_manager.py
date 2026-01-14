"""
Authentication Manager for Blissful
Handles authentication with Jellyfin, Emby, and Plex
"""

import logging
import requests as req

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authentication for request system"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def authenticate_jellyfin(self, username, password):
        """
        Authenticate with Jellyfin using admin's API key from config
        
        Args:
            username: User's Jellyfin username
            password: User's Jellyfin password
            
        Returns:
            dict: Authentication result with success status and user data
        """
        try:
            config = self.config_manager.get_config()
            jellyfin_url = config.get('jellyfin_url', '').strip()
            jellyfin_api_key = config.get('jellyfin_api_key', '').strip()
            
            logger.info(f"Attempting Jellyfin authentication for user: {username}")
            logger.info(f"Jellyfin URL: {jellyfin_url}")
            logger.info(f"API key configured: {'Yes' if jellyfin_api_key else 'No'}")
            
            # Validate configuration
            if not jellyfin_url:
                return {
                    'success': False,
                    'error': 'Jellyfin not configured. Contact admin.',
                    'status_code': 400
                }
            
            if not jellyfin_api_key:
                return {
                    'success': False,
                    'error': 'Jellyfin API key not configured. Admin must add API key in Request settings.',
                    'status_code': 400
                }
            
            if not username or not password:
                return {
                    'success': False,
                    'error': 'Username and password required',
                    'status_code': 400
                }
            
            # Make authentication request
            auth_url = f"{jellyfin_url.rstrip('/')}/Users/AuthenticateByName"
            
            payload = {
                'Username': username,
                'Pw': password
            }
            
            # Use admin's API key in headers
            headers = {
                'Content-Type': 'application/json',
                'X-Emby-Token': jellyfin_api_key,
                'X-Emby-Authorization': f'MediaBrowser Client="Blissful", Device="Web", DeviceId="blissful-web", Version="1.0.0", Token="{jellyfin_api_key}"'
            }
            
            try:
                response = req.post(auth_url, json=payload, headers=headers, timeout=30, verify=False)
                
                logger.info(f"Jellyfin response status: {response.status_code}")
                
                if response.status_code == 200:
                    auth_data = response.json()
                    access_token = auth_data.get('AccessToken')
                    user_data = auth_data.get('User', {})
                    
                    logger.info(f"✅ Authentication successful for user: {username}")
                    
                    return {
                        'success': True,
                        'access_token': access_token,
                        'username': user_data.get('Name'),
                        'user_id': user_data.get('Id'),
                        'status_code': 200
                    }
                elif response.status_code == 401:
                    logger.warning(f"❌ Invalid credentials for user: {username}")
                    return {
                        'success': False,
                        'error': 'Invalid username or password',
                        'status_code': 401
                    }
                else:
                    logger.error(f"❌ Jellyfin error {response.status_code}: {response.text[:200]}")
                    return {
                        'success': False,
                        'error': f'Jellyfin server error ({response.status_code}). Please try again or contact admin.',
                        'status_code': 500
                    }
                    
            except req.exceptions.Timeout:
                logger.error(f"Jellyfin server timeout at {jellyfin_url}")
                return {
                    'success': False,
                    'error': 'Server timeout. Please try again.',
                    'status_code': 504
                }
                
            except req.exceptions.ConnectionError as e:
                logger.error(f"Cannot connect to Jellyfin: {e}")
                return {
                    'success': False,
                    'error': 'Cannot connect to Jellyfin server',
                    'status_code': 503
                }
                
            except req.exceptions.SSLError as e:
                logger.error(f"SSL error: {e}")
                return {
                    'success': False,
                    'error': 'SSL/HTTPS error. Contact admin.',
                    'status_code': 500
                }
                
        except Exception as e:
            logger.error(f"Jellyfin authentication error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Authentication error: {str(e)}',
                'status_code': 500
            }
    
    def authenticate_emby(self, username, password):
        """
        Authenticate with Emby using admin's API key from config
        
        Args:
            username: User's Emby username
            password: User's Emby password
            
        Returns:
            dict: Authentication result with success status and user data
        """
        try:
            config = self.config_manager.get_config()
            emby_url = config.get('emby_url', '').strip()
            emby_api_key = config.get('emby_api_key', '').strip()
            
            logger.info(f"Attempting Emby authentication for user: {username}")
            logger.info(f"Emby URL: {emby_url}")
            logger.info(f"API key configured: {'Yes' if emby_api_key else 'No'}")
            
            # Validate configuration
            if not emby_url:
                return {
                    'success': False,
                    'error': 'Emby not configured. Contact admin.',
                    'status_code': 400
                }
            
            if not emby_api_key:
                return {
                    'success': False,
                    'error': 'Emby API key not configured. Admin must add API key in Request settings.',
                    'status_code': 400
                }
            
            if not username or not password:
                return {
                    'success': False,
                    'error': 'Username and password required',
                    'status_code': 400
                }
            
            # Make authentication request
            auth_url = f"{emby_url.rstrip('/')}/Users/AuthenticateByName"
            
            payload = {
                'Username': username,
                'Pw': password
            }
            
            # Use admin's API key in headers
            headers = {
                'Content-Type': 'application/json',
                'X-Emby-Token': emby_api_key,
                'X-Emby-Authorization': f'MediaBrowser Client="Blissful", Device="Web", DeviceId="blissful-web", Version="1.0.0", Token="{emby_api_key}"'
            }
            
            try:
                response = req.post(auth_url, json=payload, headers=headers, timeout=30, verify=False)
                
                logger.info(f"Emby response status: {response.status_code}")
                
                if response.status_code == 200:
                    auth_data = response.json()
                    access_token = auth_data.get('AccessToken')
                    user_data = auth_data.get('User', {})
                    
                    logger.info(f"✅ Authentication successful for user: {username}")
                    
                    return {
                        'success': True,
                        'access_token': access_token,
                        'username': user_data.get('Name'),
                        'user_id': user_data.get('Id'),
                        'status_code': 200
                    }
                elif response.status_code == 401:
                    logger.warning(f"❌ Invalid credentials for user: {username}")
                    return {
                        'success': False,
                        'error': 'Invalid username or password',
                        'status_code': 401
                    }
                else:
                    logger.error(f"❌ Emby error {response.status_code}: {response.text[:200]}")
                    return {
                        'success': False,
                        'error': f'Emby server error ({response.status_code})',
                        'status_code': 500
                    }
                    
            except req.exceptions.Timeout:
                logger.error(f"Emby server timeout at {emby_url}")
                return {
                    'success': False,
                    'error': 'Server timeout. Please try again.',
                    'status_code': 504
                }
                
            except req.exceptions.ConnectionError as e:
                logger.error(f"Cannot connect to Emby: {e}")
                return {
                    'success': False,
                    'error': 'Cannot connect to Emby server',
                    'status_code': 503
                }
                
            except req.exceptions.SSLError as e:
                logger.error(f"SSL error: {e}")
                return {
                    'success': False,
                    'error': 'SSL/HTTPS error',
                    'status_code': 500
                }
                
        except Exception as e:
            logger.error(f"Emby authentication error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Authentication error: {str(e)}',
                'status_code': 500
            }
    
    def authenticate_plex(self, username, password):
        """
        Authenticate with Plex and verify server access
        
        Args:
            username: User's Plex username
            password: User's Plex password
            
        Returns:
            dict: Authentication result with success status and user data
        """
        try:
            config = self.config_manager.get_config()
            plex_server_url = config.get('plex_url', '').strip()
            
            logger.info(f"Attempting Plex authentication for user: {username}")
            logger.info(f"Plex server URL: {plex_server_url}")
            
            # Validate configuration
            if not plex_server_url:
                return {
                    'success': False,
                    'error': 'Plex server URL not configured. Contact admin.',
                    'status_code': 400
                }
            
            if not username or not password:
                return {
                    'success': False,
                    'error': 'Username and password required',
                    'status_code': 400
                }
            
            # Step 1: Authenticate with Plex.tv
            auth_url = "https://plex.tv/users/sign_in.json"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Plex-Client-Identifier': 'blissful-web',
                'X-Plex-Product': 'Blissful',
                'X-Plex-Version': '1.0.0'
            }
            
            payload = {
                'user[login]': username,
                'user[password]': password
            }
            
            response = req.post(auth_url, data=payload, headers=headers, timeout=10)
            
            if response.status_code != 201:
                logger.warning(f"❌ Plex authentication failed for user: {username}")
                return {
                    'success': False,
                    'error': 'Invalid username or password',
                    'status_code': 401
                }
            
            auth_data = response.json()
            user_data = auth_data.get('user', {})
            user_auth_token = user_data.get('authToken')
            
            if not user_auth_token:
                return {
                    'success': False,
                    'error': 'Failed to get user auth token',
                    'status_code': 500
                }
            
            logger.info(f"✅ Plex.tv authentication successful for user: {username}")
            
            # Step 2: Verify user has access to the configured Plex server
            logger.info(f"Verifying server access for {username}...")
            
            try:
                # Get user's accessible servers from Plex.tv
                # Use the older v2/resources endpoint with proper parameters
                servers_url = "https://plex.tv/api/v2/resources?includeHttps=1&includeRelay=1"
                servers_headers = {
                    'X-Plex-Token': user_auth_token,
                    'Accept': 'application/json',
                    'X-Plex-Client-Identifier': 'blissful-web',
                    'X-Plex-Product': 'Blissful',
                    'X-Plex-Version': '1.0.0'
                }
                
                servers_response = req.get(servers_url, headers=servers_headers, timeout=10)
                
                logger.info(f"Plex servers API response status: {servers_response.status_code}")
                
                if servers_response.status_code != 200:
                    logger.error(f"Failed to get user's servers: {servers_response.status_code}")
                    logger.error(f"Response body: {servers_response.text[:500]}")
                    return {
                        'success': False,
                        'error': 'Could not verify server access',
                        'status_code': 500
                    }
                
                servers = servers_response.json()
                logger.info(f"Found {len(servers)} servers for user {username}")
                
                # Extract server identifier from configured URL
                # plex_server_url could be like "http://192.168.1.100:32400" or "https://plex.example.com"
                configured_host = plex_server_url.split('://')[-1].split(':')[0].lower()
                configured_port = '32400'  # Default Plex port
                if ':' in plex_server_url.split('://')[-1]:
                    configured_port = plex_server_url.split(':')[-1].split('/')[0]
                
                logger.info(f"Looking for server matching host: {configured_host}, port: {configured_port}")
                
                # Check if user has access to a server matching our configuration
                has_access = False
                server_name = None
                matched_server = None
                
                for server in servers:
                    # Only check actual Plex Media Servers (not players or other devices)
                    if server.get('provides') != 'server':
                        continue
                    
                    server_name_check = server.get('name', '')
                    connections = server.get('connections', [])
                    
                    logger.info(f"Checking server: {server_name_check} with {len(connections)} connections")
                    
                    for conn in connections:
                        conn_uri = conn.get('uri', '').lower()
                        conn_address = conn.get('address', '').lower()
                        conn_local = conn.get('local', False)
                        
                        logger.debug(f"  Connection: {conn_uri} (address: {conn_address}, local: {conn_local})")
                        
                        # Check if this connection matches our configured server
                        # Match by host/address
                        if configured_host in conn_uri or configured_host in conn_address:
                            has_access = True
                            server_name = server_name_check
                            matched_server = server
                            logger.info(f"✅ Match found! Server: {server_name}, Connection: {conn_uri}")
                            break
                        
                        # Also try matching the full URL
                        if plex_server_url.lower() in conn_uri:
                            has_access = True
                            server_name = server_name_check
                            matched_server = server
                            logger.info(f"✅ Match found by full URL! Server: {server_name}")
                            break
                    
                    if has_access:
                        break
                
                if not has_access:
                    logger.warning(f"❌ User {username} does not have access to the configured Plex server")
                    logger.warning(f"Configured: {plex_server_url}")
                    logger.warning(f"User has access to {len([s for s in servers if s.get('provides') == 'server'])} server(s)")
                    return {
                        'success': False,
                        'error': 'You do not have access to this Plex server. Contact the administrator.',
                        'status_code': 403
                    }
                
                logger.info(f"✅ User {username} verified to have access to server: {server_name}")
                
                return {
                    'success': True,
                    'access_token': user_auth_token,
                    'username': user_data.get('username'),
                    'user_id': user_data.get('id'),
                    'server_name': server_name,
                    'status_code': 200
                }
                
            except req.exceptions.Timeout:
                logger.error(f"Timeout checking Plex server access")
                return {
                    'success': False,
                    'error': 'Timeout verifying server access',
                    'status_code': 504
                }
            except req.exceptions.ConnectionError as e:
                logger.error(f"Cannot connect to Plex: {e}")
                return {
                    'success': False,
                    'error': 'Cannot connect to Plex servers',
                    'status_code': 503
                }
                
        except Exception as e:
            logger.error(f"Plex authentication error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }
