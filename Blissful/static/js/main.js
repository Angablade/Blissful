/**
 * Main Application Entry Point
 * Initializes the application when the page loads
 */

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
    console.log('🎵 Blissful initializing...');
    
    try {
        // Run initialization tasks
        await checkHealth();
        await loadConfiguration();
        await loadSupportedSources();
        updateQualityPresets();
        
        console.log('✅ Blissful initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing Blissful:', error);
        showNotification('Error initializing application', 'error');
    }
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showNotification('An unexpected error occurred', 'error');
});

// Prevent form submission on enter
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
        const form = e.target.closest('form');
        if (form && form.id !== 'searchForm') {
            e.preventDefault();
        }
    }
});

console.log('🎵 Blissful script loaded');
