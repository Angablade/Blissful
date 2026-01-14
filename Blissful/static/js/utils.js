/**
 * Utility Functions
 * Common utilities used across the application
 */

// Show notification to user
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Tab switching
function openTab(evt, tabName) {
    const tabContents = document.getElementsByClassName('tab-content');
    for (let content of tabContents) {
        content.classList.remove('active');
    }
    
    const tabButtons = document.getElementsByClassName('tab-button');
    for (let button of tabButtons) {
        button.classList.remove('active');
    }
    
    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');
}

// Health check
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        document.getElementById('serviceStatus').textContent = data.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy';
        document.getElementById('ffmpegStatus').textContent = data.ffmpeg_available ? '✅ Available' : '❌ Not Found';
        document.getElementById('ytdlpStatus').textContent = data.ytdlp_available ? '✅ Available' : '❌ Not Found';
    } catch (error) {
        console.error('Error checking health:', error);
        document.getElementById('serviceStatus').textContent = '❌ Error';
    }
}

// Toggle collapsible sections
function toggleSection(sectionId) {
    const content = document.getElementById(sectionId);
    const header = content.previousElementSibling;
    
    if (content.classList.contains('expanded')) {
        content.classList.remove('expanded');
        header.classList.add('collapsed');
    } else {
        content.classList.add('expanded');
        header.classList.remove('collapsed');
    }
}
