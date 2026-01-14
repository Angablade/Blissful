/**
 * Path Mapping Management
 * Handles path mapping between Lidarr and microservice
 */

let pathMappingCounter = 0;

// Add path mapping
function addPathMapping(lidarrPath = '', microPath = '') {
    const container = document.getElementById('pathMappings');
    const id = pathMappingCounter++;
    
    const mappingDiv = document.createElement('div');
    mappingDiv.className = 'path-mapping-item';
    mappingDiv.id = `mapping-${id}`;
    mappingDiv.innerHTML = `
        <input type="text" placeholder="Lidarr Path (e.g., /music)" value="${lidarrPath}" class="lidarr-path">
        <span>→</span>
        <input type="text" placeholder="Microservice Path (e.g., C:/Music)" value="${microPath}" class="micro-path">
        <button type="button" class="btn-remove" onclick="removePathMapping(${id})">✕</button>
    `;
    
    container.appendChild(mappingDiv);
}

// Remove path mapping
function removePathMapping(id) {
    const element = document.getElementById(`mapping-${id}`);
    if (element) {
        element.remove();
    }
}

// Get all path mappings
function getPathMappings() {
    const mappings = {};
    document.querySelectorAll('.path-mapping-item').forEach(mapping => {
        const lidarrPath = mapping.querySelector('.lidarr-path').value.trim();
        const microPath = mapping.querySelector('.micro-path').value.trim();
        
        if (lidarrPath && microPath) {
            mappings[microPath] = lidarrPath;
        }
    });
    return mappings;
}

// Auto-populate path mappings from Lidarr
async function autoPopulatePathMapping() {
    const lidarrUrlField = document.getElementById('lidarrUrl');
    const apiKeyField = document.getElementById('lidarrApiKey');
    
    let lidarrUrl = lidarrUrlField.value.trim();
    let lidarrApiKey = apiKeyField.value.trim();
    
    // If API key field is empty but we have a saved key, fetch it
    if (!lidarrApiKey && apiKeyField.dataset.hasSavedKey === 'true') {
        try {
            const response = await fetch('/api/get-api-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lidarr_url: lidarrUrl })
            });
            const data = await response.json();
            if (data.success && data.api_key) {
                lidarrApiKey = data.api_key;
            }
        } catch (error) {
            showNotification('Error retrieving API key', 'error');
            return;
        }
    }
    
    if (!lidarrUrl || !lidarrApiKey) {
        showNotification('Please configure Lidarr connection first', 'warning');
        openTab({ currentTarget: document.querySelector('.tab-button') }, 'lidarr-tab');
        return;
    }
    
    showNotification('Detecting paths from Lidarr...', 'info');
    
    try {
        const response = await fetch('/api/lidarr-paths', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lidarr_url: lidarrUrl,
                lidarr_api_key: lidarrApiKey
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('pathMappings');
            if (confirm(`Found ${data.paths.length} path(s) in Lidarr. Clear existing mappings and add these?`)) {
                container.innerHTML = '';
                
                data.paths.forEach(path => {
                    addPathMapping(path.lidarr_path, path.suggested_local_path || path.lidarr_path);
                });
                
                showNotification(`Added ${data.paths.length} path mapping(s)`, 'success');
            }
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error auto-detecting paths:', error);
        showNotification('Failed to detect paths from Lidarr', 'error');
    }
}
