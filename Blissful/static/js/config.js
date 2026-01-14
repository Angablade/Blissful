/**
 * Configuration Management
 * Handles loading, saving, and validating configuration
 */

// Quality presets for different formats
const qualityPresets = {
    mp3: [
        { value: '128k', label: '128 kbps - Low Quality' },
        { value: '192k', label: '192 kbps - Medium Quality' },
        { value: '256k', label: '256 kbps - High Quality' },
        { value: '320k', label: '320 kbps - Maximum Quality (Recommended)' }
    ],
    opus: [
        { value: '96k', label: '96 kbps - Good Quality' },
        { value: '128k', label: '128 kbps - High Quality' },
        { value: '192k', label: '192 kbps - Very High Quality' },
        { value: '256k', label: '256 kbps - Maximum Quality (Recommended)' }
    ],
    aac: [
        { value: '128k', label: '128 kbps - Medium Quality' },
        { value: '192k', label: '192 kbps - High Quality' },
        { value: '256k', label: '256 kbps - Very High Quality' },
        { value: '320k', label: '320 kbps - Maximum Quality (Recommended)' }
    ],
    ogg: [
        { value: 'q5', label: 'Quality 5 - Good (~160 kbps)' },
        { value: 'q7', label: 'Quality 7 - High (~224 kbps)' },
        { value: 'q9', label: 'Quality 9 - Very High (~320 kbps)' },
        { value: 'q10', label: 'Quality 10 - Maximum (Recommended)' }
    ],
    flac: [
        { value: '0', label: 'Compression Level 0 - Fast' },
        { value: '5', label: 'Compression Level 5 - Balanced' },
        { value: '8', label: 'Compression Level 8 - Maximum (Recommended)' }
    ],
    wav: [
        { value: 'pcm_s16le', label: '16-bit PCM (Standard)' },
        { value: 'pcm_s24le', label: '24-bit PCM (High Resolution)' },
        { value: 'pcm_s32le', label: '32-bit PCM (Maximum)' }
    ]
};

// Update quality presets based on format
function updateQualityPresets() {
    const format = document.getElementById('outputFormat').value;
    const qualitySelect = document.getElementById('quality');
    const qualityHelp = document.getElementById('qualityHelp');
    const currentValue = qualitySelect.value;
    
    qualitySelect.innerHTML = '';
    
    const presets = qualityPresets[format] || qualityPresets.mp3;
    presets.forEach(preset => {
        const option = document.createElement('option');
        option.value = preset.value;
        option.textContent = preset.label;
        qualitySelect.appendChild(option);
    });
    
    // Try to maintain selection if possible
    if (currentValue && Array.from(qualitySelect.options).some(opt => opt.value === currentValue)) {
        qualitySelect.value = currentValue;
    } else {
        // Select the recommended (last) option
        qualitySelect.selectedIndex = qualitySelect.options.length - 1;
    }
    
    // Update help text
    if (format === 'flac' || format === 'wav') {
        qualityHelp.textContent = 'Lossless format - no quality loss';
    } else {
        qualityHelp.textContent = 'Higher quality = larger file size';
    }
}

// Load configuration
async function loadConfiguration() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('lidarrUrl').value = config.lidarr_url || '';
        
        // Don't overwrite API key field if it's masked - just leave it empty so user can enter new one
        const apiKeyField = document.getElementById('lidarrApiKey');
        if (config.lidarr_api_key === '***MASKED***') {
            apiKeyField.placeholder = 'API Key configured (enter new key to change)';
            apiKeyField.value = '';  // Leave empty
            // Store the fact that we have an existing key
            apiKeyField.dataset.hasSavedKey = 'true';
        } else {
            apiKeyField.value = config.lidarr_api_key || '';
            apiKeyField.placeholder = 'Your Lidarr API Key';
            apiKeyField.dataset.hasSavedKey = 'false';
        }
        
        document.getElementById('outputFormat').value = config.output_format || 'mp3';
        updateQualityPresets();
        document.getElementById('quality').value = config.quality || '320k';
        
        // Audio processing options
        document.getElementById('normalizeAudio').checked = config.normalize_audio || false;
        document.getElementById('monoAudio').checked = config.mono_audio || false;
        document.getElementById('sampleRate').value = config.sample_rate || 'original';
        document.getElementById('removeSilence').checked = config.remove_silence || false;
        document.getElementById('loudnessNorm').checked = config.loudness_normalization || false;
        document.getElementById('channels').value = config.channels || 'original';
        
        // File management options
        document.getElementById('autoCleanup').checked = config.auto_cleanup !== false;
        document.getElementById('embedMetadata').checked = config.embed_metadata !== false;
        document.getElementById('embedThumbnail').checked = config.embed_thumbnail !== false;
        
        // Load path mappings
        const pathMappings = config.lidarr_path_mapping || {};
        Object.entries(pathMappings).forEach(([microPath, lidarrPath]) => {
            addPathMapping(lidarrPath, microPath);
        });
        
        // Load source priorities
        const priorities = config.source_priorities || [];
        loadSourcePriorities(priorities);
        
        // Load request system settings
        document.getElementById('enableRequests').checked = config.enable_requests || false;
        document.getElementById('autoMonitorRequests').checked = config.auto_monitor_requests || false;
        document.getElementById('enableJellyfin').checked = config.enable_jellyfin || false;
        document.getElementById('jellyfinUrl').value = config.jellyfin_url || '';
        document.getElementById('jellyfinApiKey').value = config.jellyfin_api_key || '';
        document.getElementById('enableEmby').checked = config.enable_emby || false;
        document.getElementById('embyUrl').value = config.emby_url || '';
        document.getElementById('embyApiKey').value = config.emby_api_key || '';
        document.getElementById('enablePlex').checked = config.enable_plex || false;
        document.getElementById('plexUrl').value = config.plex_url || '';
        document.getElementById('requestDefaultMonitored').value = config.request_default_monitored || 'false';
        document.getElementById('requestSearchMissing').value = config.request_search_missing || 'false';
        
    } catch (error) {
        console.error('Error loading configuration:', error);
        showNotification('Error loading configuration', 'error');
    }
}

// Save configuration
async function saveConfiguration() {
    try {
        showNotification('Saving configuration...', 'info');
        
        const apiKeyField = document.getElementById('lidarrApiKey');
        const apiKeyValue = apiKeyField.value.trim();
        
        // Build config object - ALWAYS include lidarr_api_key
        const config = {
            lidarr_url: document.getElementById('lidarrUrl').value,
            lidarr_api_key: apiKeyValue || '',  // Always send it, empty string if no value
            output_format: document.getElementById('outputFormat').value,
            quality: document.getElementById('quality').value,
            
            // Audio processing
            normalize_audio: document.getElementById('normalizeAudio').checked,
            mono_audio: document.getElementById('monoAudio').checked,
            sample_rate: document.getElementById('sampleRate').value,
            remove_silence: document.getElementById('removeSilence').checked,
            loudness_normalization: document.getElementById('loudnessNorm').checked,
            channels: document.getElementById('channels').value,
            
            // File management
            auto_cleanup: document.getElementById('autoCleanup').checked,
            embed_metadata: document.getElementById('embedMetadata').checked,
            embed_thumbnail: document.getElementById('embedThumbnail').checked,
            
            lidarr_path_mapping: getPathMappings(),
            source_priorities: getSourcePriorities(),
            
            // Request system settings
            enable_requests: document.getElementById('enableRequests').checked,
            auto_monitor_requests: document.getElementById('autoMonitorRequests').checked,
            enable_jellyfin: document.getElementById('enableJellyfin').checked,
            jellyfin_url: document.getElementById('jellyfinUrl').value,
            jellyfin_api_key: document.getElementById('jellyfinApiKey').value,
            enable_emby: document.getElementById('enableEmby').checked,
            emby_url: document.getElementById('embyUrl').value,
            emby_api_key: document.getElementById('embyApiKey').value,
            enable_plex: document.getElementById('enablePlex').checked,
            plex_url: document.getElementById('plexUrl').value,
            request_default_monitored: document.getElementById('requestDefaultMonitored').value === 'true',
            request_search_missing: document.getElementById('requestSearchMissing').value === 'true'
        };
        
        // Special marker: if field is empty but we have a saved key, send special marker
        if (!apiKeyValue && apiKeyField.dataset.hasSavedKey === 'true') {
            config.lidarr_api_key = '***KEEP_EXISTING***';
        }
        
        console.log('Saving configuration:', { 
            ...config, 
            lidarr_api_key: config.lidarr_api_key === '***KEEP_EXISTING***' ? '(keeping existing)' : 
                           config.lidarr_api_key ? '***' : '(empty)' 
        });
        
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Configuration saved successfully!', 'success');
            
            // If we saved a new API key, update the dataset
            if (apiKeyValue) {
                apiKeyField.dataset.hasSavedKey = 'true';
                apiKeyField.placeholder = 'API Key configured (enter new key to change)';
                apiKeyField.value = '';  // Clear the field for security
            }
        } else {
            showNotification('❌ Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        showNotification('❌ Failed to save: ' + error.message, 'error');
    }
}

// Test Lidarr connection
async function testLidarrConnection() {
    const urlField = document.getElementById('lidarrUrl');
    const apiKeyField = document.getElementById('lidarrApiKey');
    const resultDiv = document.getElementById('connectionResult');
    
    let url = urlField.value.trim();
    let apiKey = apiKeyField.value.trim();
    
    // If API key field is empty but we have a saved key, fetch it from backend
    if (!apiKey && apiKeyField.dataset.hasSavedKey === 'true') {
        resultDiv.className = 'message info';
        resultDiv.textContent = 'Loading saved API key...';
        
        try {
            // Get the actual API key from backend for testing
            const response = await fetch('/api/get-api-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lidarr_url: url })
            });
            
            const data = await response.json();
            if (data.success && data.api_key) {
                apiKey = data.api_key;
            } else {
                resultDiv.className = 'message error';
                resultDiv.textContent = '❌ Could not retrieve saved API key';
                return;
            }
        } catch (error) {
            resultDiv.className = 'message error';
            resultDiv.textContent = '❌ Error retrieving API key';
            return;
        }
    }
    
    if (!url || !apiKey) {
        resultDiv.className = 'message error';
        resultDiv.textContent = 'Please enter both URL and API key';
        return;
    }
    
    resultDiv.className = 'message info';
    resultDiv.textContent = 'Testing connection...';
    
    try {
        const response = await fetch('/api/test-lidarr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lidarr_url: url, lidarr_api_key: apiKey })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.className = 'message success';
            resultDiv.textContent = '✅ ' + data.message;
        } else {
            resultDiv.className = 'message error';
            resultDiv.textContent = '❌ ' + data.error;
        }
    } catch (error) {
        console.error('Error testing connection:', error);
        resultDiv.className = 'message error';
        resultDiv.textContent = '❌ Connection failed: ' + error.message;
    }
}
