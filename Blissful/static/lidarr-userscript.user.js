// ==UserScript==
// @name         Blissful - Lidarr Music Downloader
// @namespace    http://tampermonkey.net/
// @version      1.4.0
// @description  Download missing tracks, albums, or everything from Lidarr using Blissful microservice
// @author       Blissful
// @match        http://localhost:8686/*
// @match        https://localhost:8686/*
// @match        http://127.0.0.1:8686/*
// @match        https://127.0.0.1:8686/*
// @grant        GM.xmlHttpRequest
// @grant        GM_xmlhttpRequest
// @grant        GM.getValue
// @grant        GM.setValue
// @grant        GM_getValue
// @grant        GM_setValue
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    console.log('[Blissful] Script starting v1.4.0...');

    // Compatibility layer for Greasemonkey 4 and Tampermonkey
    const GM_API = {
        xmlHttpRequest: null,
        getValue: null,
        setValue: null
    };

    // Detect and setup the correct API
    if (typeof GM_xmlhttpRequest !== 'undefined') {
        // Tampermonkey (synchronous API)
        console.log('[Blissful] Detected Tampermonkey API');
        GM_API.xmlHttpRequest = GM_xmlhttpRequest;
        GM_API.getValue = (key, defaultValue) => Promise.resolve(GM_getValue(key, defaultValue));
        GM_API.setValue = (key, value) => Promise.resolve(GM_setValue(key, value));
    } else if (typeof GM !== 'undefined' && typeof GM.xmlHttpRequest !== 'undefined') {
        // Greasemonkey 4+ (async API)
        console.log('[Blissful] Detected Greasemonkey 4+ API');
        GM_API.xmlHttpRequest = GM.xmlHttpRequest;
        GM_API.getValue = GM.getValue || ((key, defaultValue) => Promise.resolve(defaultValue));
        GM_API.setValue = GM.setValue || ((key, value) => Promise.resolve());
    } else {
        console.error('[Blissful] No userscript manager API detected!');
        console.error('[Blissful] Please install Tampermonkey or Greasemonkey');
    }

    // Check if API is available
    if (!GM_API.xmlHttpRequest) {
        console.error('[Blissful] GM.xmlHttpRequest is not available!');
        console.error('[Blissful] Make sure Greasemonkey/Tampermonkey is installed and the script has correct @grant permissions');
    } else {
        console.log('[Blissful] ✓ API initialized successfully');
    }

    // Configuration
    let CONFIG = {
        microserviceUrl: 'http://localhost:7373',
        autoRetry: true,
        showNotifications: true
    };

    // Load config asynchronously
    async function loadConfig() {
        try {
            CONFIG.microserviceUrl = await GM_API.getValue('microserviceUrl', 'http://localhost:7373');
            CONFIG.autoRetry = await GM_API.getValue('autoRetry', true);
            CONFIG.showNotifications = await GM_API.getValue('showNotifications', true);
            console.log('[Blissful] Using microservice URL:', CONFIG.microserviceUrl);
        } catch (e) {
            console.log('[Blissful] Using default config:', e);
        }
    }

    // Utility: Show notification
    function showNotification(message, type = 'info') {
        if (!CONFIG.showNotifications) return;

        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 100000;
            color: white;
            font-family: system-ui, -apple-system, sans-serif;
            font-size: 14px;
            animation: slideIn 0.3s ease;
        `;
        
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            info: '#6366f1',
            warning: '#f59e0b'
        };
        notification.style.background = colors[type] || colors.info;
        notification.textContent = message;
        
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // API request helper
    function apiRequest(endpoint, data = null) {
        return new Promise((resolve, reject) => {
            if (!GM_API.xmlHttpRequest) {
                reject(new Error('GM.xmlHttpRequest not available'));
                return;
            }

            console.log('[Blissful] Making API request to:', CONFIG.microserviceUrl + endpoint);

            GM_API.xmlHttpRequest({
                method: data ? 'POST' : 'GET',
                url: `${CONFIG.microserviceUrl}${endpoint}`,
                headers: {
                    'Content-Type': 'application/json',
                },
                data: data ? JSON.stringify(data) : null,
                onload: (response) => {
                    console.log('[Blissful] API response:', response.status, response.responseText.substring(0, 200));
                    try {
                        const result = JSON.parse(response.responseText);
                        resolve(result);
                    } catch (e) {
                        console.error('[Blissful] Failed to parse response:', e);
                        reject(new Error('Invalid JSON response'));
                    }
                },
                onerror: (error) => {
                    console.error('[Blissful] Network error:', error);
                    reject(new Error('Network error'));
                },
                ontimeout: () => {
                    console.error('[Blissful] Request timeout');
                    reject(new Error('Request timeout'));
                }
            });
        });
    }

    // Download track
    async function downloadTrack(artist, title, album = '', albumId = null, trackNumber = 1) {
        console.log('[Blissful] Downloading track:', artist, '-', title, `(Track #${trackNumber})`);
        
        // Check if GM API is available
        if (!GM_API.xmlHttpRequest) {
            const errorMsg = 'Tampermonkey API not available. Please reinstall the userscript.';
            console.error('[Blissful]', errorMsg);
            showNotification(errorMsg, 'error');
            return { success: false, error: errorMsg };
        }
        
        try {
            const requestData = {
                artist,
                title,
                album
            };
            
            // Add optional parameters if available
            if (albumId) requestData.album_id = albumId;
            if (trackNumber) requestData.track_number = trackNumber;
            
            const result = await apiRequest('/api/download-track', requestData);

            if (result.success) {
                console.log('[Blissful] Download successful:', title);
                showNotification(`✓ Downloaded: ${title}`, 'success');
            } else {
                console.error('[Blissful] Download failed:', result.error);
                showNotification(`✗ Failed: ${title}`, 'error');
            }

            return result;
        } catch (error) {
            console.error('[Blissful] Error downloading:', error);
            showNotification(`Error: ${error.message}`, 'error');
            return { success: false, error: error.message };
        }
    }
    
    // Update track row status after successful download
    async function updateTrackRowStatus(row, statusCell) {
        try {
            console.log('[Blissful] Updating track row status...');
            
            // Remove the warning icon
            const warningIcon = statusCell.querySelector('[data-icon="triangle-exclamation"]');
            if (warningIcon) {
                warningIcon.remove();
            }
            
            // Add a checkmark icon (using Lidarr's existing icon classes)
            const checkIcon = document.createElement('span');
            checkIcon.setAttribute('class', 'Icon-icon-GFbI_');
            checkIcon.setAttribute('data-icon', 'check');
            checkIcon.style.color = '#10b981';
            checkIcon.innerHTML = '✓';
            statusCell.appendChild(checkIcon);
            
            // Update row styling to show it's no longer missing
            row.style.opacity = '0.7';
            
            // Wait a bit for Lidarr to detect the file, then refresh album data
            console.log('[Blissful] Waiting for Lidarr to detect file...');
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Force refresh album info from cache
            const albumId = getAlbumIdFromUrl();
            if (albumId) {
                console.log('[Blissful] Refreshing album info...');
                await extractAlbumInfo(true); // Force refresh
            }
            
            console.log('[Blissful] ✓ Track row updated successfully');
        } catch (error) {
            console.error('[Blissful] Error updating track row:', error);
        }
    }

    // Download album
    async function downloadAlbum(artist, album, tracks) {
        console.log('[Blissful] Downloading album:', artist, '-', album, `(${tracks.length} tracks)`);
        showNotification(`Starting: ${album} (${tracks.length} tracks)`, 'info');

        try {
            const result = await apiRequest('/api/download-album', {
                artist,
                album,
                tracks: tracks.map(t => ({ title: t.title }))
            });

            if (result.success) {
                console.log('[Blissful] Album download complete:', result);
                showNotification(
                    `✓ Complete: ${result.successful}/${result.total_tracks} tracks`,
                    result.failed > 0 ? 'warning' : 'success'
                );
            } else {
                console.error('[Blissful] Album download failed:', result.error);
                showNotification(`✗ Failed: ${result.error}`, 'error');
            }

            return result;
        } catch (error) {
            console.error('[Blissful] Error:', error);
            showNotification(`Error: ${error.message}`, 'error');
            return { success: false, error: error.message };
        }
    }

    // Create download button
    function createButton(text, onClick) {
        const btn = document.createElement('button');
        btn.style.cssText = `
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            margin: 10px 5px;
            font-family: system-ui, -apple-system, sans-serif;
            font-size: 14px;
            transition: all 0.3s;
        `;
        btn.textContent = text;
        btn.addEventListener('click', onClick);
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-2px)';
            btn.style.boxShadow = '0 4px 12px rgba(99, 102, 241, 0.4)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0)';
            btn.style.boxShadow = 'none';
        });
        return btn;
    }

    // Cache for album info to avoid repeated API calls
    let cachedAlbumInfo = null;
    let lastAlbumId = null;

    // Extract album ID from URL
    function getAlbumIdFromUrl() {
        const match = window.location.pathname.match(/\/album\/([a-f0-9-]+)/);
        return match ? match[1] : null;
    }

    // Extract album info via backend microservice
    async function extractAlbumInfo(forceRefresh = false) {
        const albumId = getAlbumIdFromUrl();
        if (!albumId) {
            console.log('[Blissful] Not on an album page');
            return null;
        }
        
        // Check cache
        if (!forceRefresh && cachedAlbumInfo && lastAlbumId === albumId) {
            console.log('[Blissful] Using cached album info:', cachedAlbumInfo);
            return cachedAlbumInfo;
        }
        
        // Reset cache if album changed
        if (lastAlbumId !== albumId) {
            cachedAlbumInfo = null;
            lastAlbumId = albumId;
        }
        
        console.log('[Blissful] Fetching album info from microservice for:', albumId);
        
        try {
            // Call microservice API to get album info
            const result = await apiRequest(`/api/album-info/${albumId}`);
            
            if (result.success) {
                const albumInfo = {
                    title: result.title,
                    artist: result.artist,
                    foreignAlbumId: result.foreignAlbumId,
                    lidarrAlbumId: result.lidarrAlbumId || null
                };
                
                console.log('[Blissful] ✓ Album info from microservice:', albumInfo);
                
                // Cache the result
                cachedAlbumInfo = albumInfo;
                return albumInfo;
            } else {
                console.error('[Blissful] Microservice returned error:', result.error);
                return null;
            }
            
        } catch (error) {
            console.error('[Blissful] Error fetching album info from microservice:', error);
            return null;
        }
    }

    // Inject download icons in album search cells (artist page, wanted/missing)
    function injectAlbumIcons() {
        console.log('[Blissful] Injecting album download icons...');
        console.log('[Blissful] Current pathname:', window.location.pathname);
        
        // Find all album search cells - these contain the search buttons
        const cells = document.querySelectorAll('[class*="AlbumSearchCell"]');
        console.log('[Blissful] Found', cells.length, 'album search cells');

        if (cells.length === 0) {
            console.log('[Blissful] No AlbumSearchCell found, trying alternate selectors...');
            const allCells = document.querySelectorAll('td');
            console.log('[Blissful] Total td elements:', allCells.length);
            const searchButtonCells = Array.from(allCells).filter(td => 
                td.querySelector('button[title*="Search"]') || 
                td.querySelector('[data-icon="magnifying-glass"]')
            );
            console.log('[Blissful] Cells with search buttons:', searchButtonCells.length);
        }

        let iconsAdded = 0;
        const isWantedMissingPage = window.location.pathname.includes('/wanted/missing');

        cells.forEach((cell, index) => {
            console.log(`[Blissful] Processing cell ${index + 1}/${cells.length}`);
            
            // Skip if already has Blissful icon
            if (cell.querySelector('.blissful-album-icon')) {
                console.log(`[Blissful] Cell ${index + 1} already has icon, skipping`);
                return;
            }

            // Get the row
            const row = cell.closest('tr');
            if (!row) {
                console.log(`[Blissful] Cell ${index + 1} has no parent row`);
                return;
            }

            // Debug: log row text content
            console.log(`[Blissful] Row ${index + 1} text:`, row.textContent.substring(0, 100));

            let hasMissing = false;
            
            if (isWantedMissingPage) {
                // On wanted/missing page, ALL albums are missing by definition
                // Just check that we can find an album link
                hasMissing = !!row.querySelector('a[href*="/album/"]');
                console.log(`[Blissful] Wanted/missing row ${index + 1}: hasMissing = ${hasMissing}`);
            } else {
                // On artist page, check status label for "0 / X" pattern
                const statusLabel = row.querySelector('[class*="Label"]');
                console.log(`[Blissful] Row ${index + 1} status label:`, statusLabel?.textContent);
                hasMissing = statusLabel && statusLabel.textContent.match(/0\s*\/\s*\d+/);
            }

            if (!hasMissing) {
                console.log(`[Blissful] Row ${index + 1} is not missing`);
                return;
            }

            // Extract album info from row
            const albumLink = row.querySelector('a[href*="/album/"]');
            if (!albumLink) {
                console.log(`[Blissful] Row ${index + 1} has no album link`);
                return;
            }

            const albumTitle = albumLink.textContent.trim();
            const albumUrl = albumLink.href;
            
            // Extract artist name
            const artistLink = row.querySelector('a[href*="/artist/"]');
            const artistName = artistLink ? artistLink.textContent.trim() : '';
            
            console.log('[Blissful] Adding icon for missing album:', albumTitle, 'by', artistName || 'Unknown');

            // Create download icon button (styled like Lidarr's buttons)
            const iconButton = document.createElement('button');
            iconButton.className = 'blissful-album-icon IconButton-button-t4C5V Link-link-RInnp';
            iconButton.setAttribute('aria-label', 'Download with Blissful');
            iconButton.setAttribute('title', `Download missing tracks from ${albumTitle}`);
            iconButton.setAttribute('type', 'button');
            iconButton.innerHTML = '🎵';
            iconButton.style.cssText = `
                cursor: pointer;
                font-size: 12px;
                padding: 0;
                border: none;
                border-radius: 3px;
                width: 24px;
                height: 24px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin: 0 2px;
                transition: all 0.2s;
                vertical-align: middle;
            `;
            
            iconButton.addEventListener('mouseenter', () => {
                iconButton.style.transform = 'scale(1.1)';
                iconButton.style.boxShadow = '0 2px 8px rgba(99, 102, 241, 0.5)';
            });
            
            iconButton.addEventListener('mouseleave', () => {
                iconButton.style.transform = 'scale(1)';
                iconButton.style.boxShadow = 'none';
            });
            
            iconButton.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Don't navigate - instead show a message that this will be implemented
                showNotification(`Album download coming soon! For now, visit the album page to download individual tracks.`, 'info');
                
                // TODO: Implement album-level download API call
                // For now, navigate to album page
                setTimeout(() => {
                    window.location.href = albumUrl;
                }, 1500);
            });

            // Insert icon button after the existing search buttons
            cell.appendChild(iconButton);
            iconsAdded++;
            console.log('[Blissful] ✓ Album icon added for:', albumTitle);
        });

        console.log(`[Blissful] Total icons added: ${iconsAdded}`);
    }

    // Inject download icons in track actions cells (album track list)
    async function injectTrackActionIcons() {
        console.log('[Blissful] Injecting track action icons...');
        console.log('[Blissful] Current pathname:', window.location.pathname);
        
        // First, try to extract album info - if it fails, don't add icons yet
        const albumInfo = await extractAlbumInfo();
        if (!albumInfo) {
            console.log('[Blissful] Album info not available yet, will retry on next mutation');
            return;
        }
        
        console.log('[Blissful] ✓ Album info available:', albumInfo);
        
        // Find all track actions cells
        const cells = document.querySelectorAll('[class*="TrackActionsCell"]');
        console.log('[Blissful] Found', cells.length, 'track action cells');

        if (cells.length === 0) {
            console.log('[Blissful] No TrackActionsCell found, trying alternate selectors...');
            // Debug: check for track rows
            const trackRows = document.querySelectorAll('[class*="TrackRow"]');
            console.log('[Blissful] Found', trackRows.length, 'track rows');
            const missingIcons = document.querySelectorAll('[data-icon="triangle-exclamation"]');
            console.log('[Blissful] Found', missingIcons.length, 'missing/warning icons');
            return; // Don't proceed if no cells found
        }

        let iconsAdded = 0;

        cells.forEach((cell, index) => {
            console.log(`[Blissful] Processing track cell ${index + 1}/${cells.length}`);
            
            // Skip if already has Blissful icon
            if (cell.querySelector('.blissful-track-action-icon')) {
                console.log(`[Blissful] Track cell ${index + 1} already has icon`);
                return;
            }

            // Get the row
            const row = cell.closest('tr');
            if (!row) {
                console.log(`[Blissful] Track cell ${index + 1} has no parent row`);
                return;
            }

            // Debug: log row classes and text
            console.log(`[Blissful] Track row ${index + 1} classes:`, row.className);
            console.log(`[Blissful] Track row ${index + 1} text:`, row.textContent.substring(0, 100));

            // Check if this track is missing by looking for the warning icon in status cell
            const statusCell = row.querySelector('[class*="TrackRow-status"]');
            const hasWarningIcon = statusCell && statusCell.querySelector('[data-icon="triangle-exclamation"]');
            
            console.log(`[Blissful] Track row ${index + 1} has warning icon:`, !!hasWarningIcon);

            if (!hasWarningIcon) {
                console.log(`[Blissful] Track row ${index + 1} is not missing`);
                return;
            }

            // Extract track info
            const titleCell = row.querySelector('[class*="TrackRow-title"]');
            if (!titleCell) {
                console.log(`[Blissful] Track row ${index + 1} has no title cell`);
                return;
            }

            const title = titleCell.textContent.trim();
            if (!title || title.length === 0) {
                console.log(`[Blissful] Track row ${index + 1} has empty title`);
                return;
            }

            // Extract track number
            const trackNumCell = row.querySelector('[class*="TrackRow-trackNumber"]');
            const trackNum = trackNumCell ? trackNumCell.textContent.trim() : '';

            console.log('[Blissful] Adding action icon for missing track:', trackNum, title, '- Album:', albumInfo.title, '- Artist:', albumInfo.artist);

            // Create download icon button (styled like Lidarr's buttons)
            const iconButton = document.createElement('button');
            iconButton.className = 'blissful-track-action-icon IconButton-button-t4C5V Link-link-RInnp';
            iconButton.setAttribute('aria-label', 'Download with Blissful');
            iconButton.setAttribute('title', 'Download with Blissful');
            iconButton.setAttribute('type', 'button');
            iconButton.innerHTML = '🎵';
            iconButton.style.cssText = `
                cursor: pointer;
                font-size: 12px;
                padding: 0;
                border: none;
                border-radius: 3px;
                width: 24px;
                height: 24px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin: 0 2px;
                transition: all 0.2s;
                vertical-align: middle;
            `;
            
            iconButton.addEventListener('mouseenter', () => {
                iconButton.style.transform = 'scale(1.1)';
                iconButton.style.boxShadow = '0 2px 8px rgba(99, 102, 241, 0.5)';
            });
            
            iconButton.addEventListener('mouseleave', () => {
                iconButton.style.transform = 'scale(1)';
                iconButton.style.boxShadow = 'none';
            });
            
            iconButton.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                iconButton.innerHTML = '⏳';
                iconButton.style.cursor = 'wait';
                iconButton.disabled = true;
                
                // Extract album ID and track number
                const albumId = cachedAlbumInfo?.lidarrAlbumId;
                const trackNumber = parseInt(trackNum) || 1;
                
                const result = await downloadTrack(
                    albumInfo.artist,
                    title,
                    albumInfo.title,
                    albumId,
                    trackNumber
                );
                
                if (result.success) {
                    iconButton.innerHTML = '✓';
                    iconButton.style.background = '#10b981';
                    
                    // Update the track row to show it's now available
                    await updateTrackRowStatus(row, statusCell);
                    
                    setTimeout(() => {
                        iconButton.remove();
                    }, 2000);
                } else {
                    iconButton.innerHTML = '✗';
                    iconButton.style.background = '#ef4444';
                    iconButton.style.cursor = 'pointer';
                    iconButton.disabled = false;
                }
            });

            // Insert icon button into the cell
            cell.appendChild(iconButton);
            iconsAdded++;
            console.log('[Blissful] ✓ Track action icon added for:', title);
        });

        console.log(`[Blissful] Total track icons added: ${iconsAdded}`);
    }

    // Initialize
    async function init() {
        console.log('[Blissful] Initializing userscript v1.4.0');
        console.log('[Blissful] Page URL:', window.location.href);
        console.log('[Blissful] DOM state:', document.readyState);

        await loadConfig();

        // Injection function based on page type
        function injectIcons() {
            if (window.location.pathname.includes('/wanted/missing') || 
                window.location.pathname.includes('/artist/')) {
                // Album list pages - inject album icons
                injectAlbumIcons();
            } else if (window.location.pathname.includes('/album/')) {
                // Album detail page - inject track action icons
                injectTrackActionIcons();
            }
        }

        // Wait for page to be ready
        if (document.readyState === 'loading') {
            console.log('[Blissful] Waiting for DOM to load...');
            document.addEventListener('DOMContentLoaded', () => {
                console.log('[Blissful] DOM loaded, injecting icons...');
                setTimeout(injectIcons, 2000); // Increased delay for SPA
            });
        } else {
            console.log('[Blissful] DOM already loaded, injecting icons...');
            setTimeout(injectIcons, 2000); // Increased delay for SPA
        }

        // Watch for dynamic content changes
        const observer = new MutationObserver(() => {
            injectIcons();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        console.log('[Blissful] ✓ Initialized successfully');
    }

    // Start
    init();
})();
