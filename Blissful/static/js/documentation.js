/**
 * Documentation Module
 * Handles markdown rendering and navigation for documentation tab
 */

class DocumentationViewer {
    constructor() {
        this.currentDoc = 'README';
        this.cache = new Map();
        this.init();
    }

    init() {
        // Wait for marked.js to load, or use fallback
        if (typeof marked === 'undefined') {
            console.warn('marked.js not loaded, using basic rendering');
            this.useBasicRenderer = true;
        } else {
            // Configure marked.js
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: true,
                mangle: false,
                sanitize: false,
                smartLists: true,
                smartypants: true
            });
            this.useBasicRenderer = false;
        }

        this.setupEventListeners();
        this.loadDocument('README'); // Load initial document
    }

    setupEventListeners() {
        // Documentation link clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('doc-link')) {
                e.preventDefault();
                const docName = e.target.dataset.doc;
                this.loadDocument(docName);
                
                // Update active state
                document.querySelectorAll('.doc-link').forEach(link => {
                    link.classList.remove('active');
                });
                e.target.classList.add('active');
            }
        });
    }

    async loadDocument(docName) {
        this.currentDoc = docName;
        const viewer = document.getElementById('markdown-viewer');
        
        if (!viewer) {
            console.error('Markdown viewer element not found');
            return;
        }

        // Show loading state
        viewer.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading documentation...</p>
            </div>
        `;

        try {
            // Check cache first
            if (this.cache.has(docName)) {
                this.renderMarkdown(this.cache.get(docName), viewer);
                return;
            }

            // Fetch markdown file
            const response = await fetch(`/api/docs/${docName}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const markdown = await response.text();
            
            // Cache the content
            this.cache.set(docName, markdown);
            
            // Render markdown
            this.renderMarkdown(markdown, viewer);

        } catch (error) {
            console.error('Error loading documentation:', error);
            viewer.innerHTML = `
                <div style="text-align: center; padding: 60px; color: #e74c3c;">
                    <h2>📄 Documentation Not Found</h2>
                    <p>Could not load <strong>${docName}.md</strong></p>
                    <p style="font-size: 14px; color: #666;">${error.message}</p>
                    <button onclick="documentationViewer.loadDocument('README')" 
                            style="margin-top: 20px; padding: 10px 20px; background: var(--primary-color); color: white; border: none; border-radius: 6px; cursor: pointer;">
                        Back to Overview
                    </button>
                </div>
            `;
        }
    }

    renderMarkdown(markdown, container) {
        if (this.useBasicRenderer) {
            // Fallback: Basic text rendering
            container.innerHTML = `<pre style="white-space: pre-wrap; font-family: system-ui;">${this.escapeHtml(markdown)}</pre>`;
        } else {
            // Use marked.js for proper markdown rendering
            try {
                const html = marked.parse(markdown);
                container.innerHTML = html;
                
                // Add syntax highlighting if available
                if (typeof Prism !== 'undefined') {
                    Prism.highlightAllUnder(container);
                }
                
                // Smooth scroll to top
                container.scrollTop = 0;
                
                // Handle internal documentation links
                container.querySelectorAll('a[href*="#!/documentation"]').forEach(link => {
                    const href = link.getAttribute('href');
                    const match = href.match(/doc=([^&]+)/);
                    if (match) {
                        const docName = match[1];
                        link.addEventListener('click', (e) => {
                            e.preventDefault();
                            this.loadDocument(docName);
                            
                            // Update sidebar active state
                            document.querySelectorAll('.doc-link').forEach(navLink => {
                                if (navLink.dataset.doc === docName) {
                                    document.querySelectorAll('.doc-link').forEach(l => l.classList.remove('active'));
                                    navLink.classList.add('active');
                                }
                            });
                        });
                        // Visual indicator that it's an internal link
                        link.style.cursor = 'pointer';
                    }
                });
                
                // Make external links open in new tab
                container.querySelectorAll('a[href^="http"]').forEach(link => {
                    // Skip if already handled as internal doc link
                    if (!link.getAttribute('href').includes('#!/documentation')) {
                        link.setAttribute('target', '_blank');
                        link.setAttribute('rel', 'noopener noreferrer');
                    }
                });

            } catch (error) {
                console.error('Error rendering markdown:', error);
                container.innerHTML = `<pre>${this.escapeHtml(markdown)}</pre>`;
            }
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    clearCache() {
        this.cache.clear();
    }

    reloadCurrent() {
        this.cache.delete(this.currentDoc);
        this.loadDocument(this.currentDoc);
    }
}

// Initialize documentation viewer when tab is shown
let documentationViewer = null;

function initDocumentation() {
    if (!documentationViewer) {
        documentationViewer = new DocumentationViewer();
        console.log('📚 Documentation viewer initialized');
    }
}

// Auto-initialize if documentation tab is active
document.addEventListener('DOMContentLoaded', () => {
    // Check if documentation tab exists
    const docTab = document.getElementById('documentation');
    if (docTab) {
        // Initialize when tab becomes visible
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.classList.contains('active')) {
                    initDocumentation();
                }
            });
        });

        observer.observe(docTab, {
            attributes: true,
            attributeFilter: ['class']
        });

        // Also initialize if tab is already active
        if (docTab.classList.contains('active')) {
            initDocumentation();
        }
    }
});

// Export for global access
window.documentationViewer = documentationViewer;
window.initDocumentation = initDocumentation;
