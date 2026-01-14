"""
Blissful - Lidarr Music Downloader Microservice
Main application file with modular architecture
"""

from flask import Flask
from flask_cors import CORS
import os
import logging

# Import configuration and managers from extend folder
from extend.config_manager import ConfigManager
from extend.lidarr_client import LidarrClient
from extend.download_manager import DownloadManager
from extend.audio_converter import AudioConverter
from extend.source_manager import SourceManager

# Import new modular managers
from extend.auth_manager import AuthManager
from extend.request_manager import RequestManager
from extend.album_manager import AlbumManager
from extend.track_manager import TrackManager
from extend.sources_api import SourcesAPI
from extend.system_utils import SystemUtils
from extend.routes import register_routes

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for userscript communication

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("="*60)
logger.info("🎵 Blissful - Lidarr Music Downloader")
logger.info("="*60)

# Initialize core managers
logger.info("📦 Initializing core managers...")

config_manager = ConfigManager()
download_manager = DownloadManager()
audio_converter = AudioConverter()
source_manager = SourceManager()

logger.info("✅ Core managers initialized")

# Initialize new modular managers
logger.info("🔧 Initializing modular managers...")

auth_manager = AuthManager(config_manager)
request_manager = RequestManager(config_manager, LidarrClient)
album_manager = AlbumManager(config_manager, LidarrClient, download_manager, audio_converter)
track_manager = TrackManager(config_manager, LidarrClient, download_manager, audio_converter)
sources_api = SourcesAPI(source_manager)
system_utils = SystemUtils(config_manager)

logger.info("✅ All modular managers initialized")

# Register all API routes
logger.info("🛣️  Registering API routes...")
register_routes(
    app=app,
    config_manager=config_manager,
    lidarr_client=LidarrClient,
    download_manager=download_manager,
    audio_converter=audio_converter,
    source_manager=source_manager,
    auth_manager=auth_manager,
    request_manager=request_manager,
    album_manager=album_manager,
    track_manager=track_manager,
    sources_api=sources_api,
    system_utils=system_utils
)
logger.info("✅ All routes registered successfully")

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    logger.info("🚀 Starting Flask application...")
    logger.info("")
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 7373))
    
    logger.info(f"📍 Server running at: http://localhost:{port}")
    logger.info(f"📱 Request page: http://localhost:{port}/request")
    logger.info(f"⚙️  Config page: http://localhost:{port}")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
