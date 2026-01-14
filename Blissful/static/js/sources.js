/**
 * Source Management - Simplified
 * Direct list of searchable yt-dlp sources with enable/disable and reordering
 */

let draggedItem = null;

// Load source priorities - shows ALL searchable sources
function loadSourcePriorities(priorities) {
    const container = document.getElementById('sourcePriorityList');
    container.innerHTML = '';
    
    // If no priorities configured, show all searchable sources from API
    if (priorities.length === 0) {
        // Will be populated after API loads
        setTimeout(() => {
            populateAllSearchableSources();
        }, 100);
        return;
    }
    
    priorities.forEach((source, index) => {
        const item = createSourcePriorityItem(source, index);
        container.appendChild(item);
    });
    
    updatePriorityBadges();
}

// Populate all searchable sources from API
async function populateAllSearchableSources() {
    try {
        const response = await fetch('/api/supported-sources?music_only=false');
        const data = await response.json();
        
        if (!data.success) {
            console.error('Failed to load sources');
            return;
        }
        
        // Filter to only searchable sources and sort by tier
        const searchableSources = data.sources
            .filter(source => source.search_supported)
            .sort((a, b) => {
                if (a.tier !== b.tier) return a.tier - b.tier;
                return a.name.localeCompare(b.name);
            });
        
        const container = document.getElementById('sourcePriorityList');
        container.innerHTML = '';
        
        // Add all searchable sources as enabled by default
        searchableSources.forEach((source, index) => {
            const sourceData = {
                name: source.name,
                search: source.ie_key || source.name.toLowerCase(),
                enabled: true,
                tier: source.tier,
                description: source.description
            };
            const item = createSourcePriorityItem(sourceData, index);
            container.appendChild(item);
        });
        
        updatePriorityBadges();
        console.log(`✅ Loaded ${searchableSources.length} searchable sources`);
        
    } catch (error) {
        console.error('Error loading sources:', error);
        const container = document.getElementById('sourcePriorityList');
        container.innerHTML = `
            <div class="source-placeholder">
                <span>❌</span>
                <p>Error loading sources</p>
                <button class="btn btn-secondary" onclick="populateAllSearchableSources()">🔄 Retry</button>
            </div>
        `;
    }
}

// Create source priority item
function createSourcePriorityItem(source, index) {
    const div = document.createElement('div');
    div.className = 'source-priority-item';
    div.draggable = true;
    div.dataset.index = index;
    
    div.addEventListener('dragstart', handleDragStart);
    div.addEventListener('dragover', handleDragOver);
    div.addEventListener('drop', handleDrop);
    div.addEventListener('dragend', handleDragEnd);
    
    div.innerHTML = `
        <div class="drag-handle">⋮⋮</div>
        <div class="priority-badge">${index + 1}</div>
        <div class="source-info">
            <strong>${source.name}</strong>
            <small>${source.search || source.name.toLowerCase()}</small>
        </div>
        <div class="source-controls">
            <label class="toggle-switch">
                <input type="checkbox" ${source.enabled ? 'checked' : ''} onchange="toggleSource(${index})">
                <span class="toggle-slider"></span>
            </label>
        </div>
    `;
    return div;
}

// Drag and drop handlers
function handleDragStart(e) {
    draggedItem = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    
    const container = document.getElementById('sourcePriorityList');
    const afterElement = getDragAfterElement(container, e.clientY);
    
    if (afterElement == null) {
        container.appendChild(draggedItem);
    } else {
        container.insertBefore(draggedItem, afterElement);
    }
    
    return false;
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    updatePriorityBadges();
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedItem = null;
    updatePriorityBadges();
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.source-priority-item:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Update priority badges and event handlers
function updatePriorityBadges() {
    const container = document.getElementById('sourcePriorityList');
    const items = container.querySelectorAll('.source-priority-item');
    
    items.forEach((item, index) => {
        const badge = item.querySelector('.priority-badge');
        badge.textContent = index + 1;
        
        const toggle = item.querySelector('input[type="checkbox"]');
        if (toggle) {
            toggle.onchange = () => toggleSource(index);
        }
    });
}

// Toggle source enabled/disabled
function toggleSource(index) {
    console.log(`Source ${index} toggled`);
    const items = document.querySelectorAll('.source-priority-item');
    const item = items[index];
    if (item) {
        const isEnabled = item.querySelector('input[type="checkbox"]').checked;
        if (isEnabled) {
            item.style.opacity = '1';
        } else {
            item.style.opacity = '0.6';
        }
    }
}

// Filter sources
function filterSources() {
    const filter = document.getElementById('sourceFilter').value.toLowerCase();
    const items = document.querySelectorAll('.source-priority-item');
    
    items.forEach(item => {
        const name = item.querySelector('strong').textContent.toLowerCase();
        const search = item.querySelector('small').textContent.toLowerCase();
        
        if (name.includes(filter) || search.includes(filter)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Get source priorities for saving
function getSourcePriorities() {
    const items = document.querySelectorAll('.source-priority-item');
    const priorities = [];
    
    items.forEach(item => {
        const name = item.querySelector('strong').textContent;
        const search = item.querySelector('small').textContent;
        const enabled = item.querySelector('input[type="checkbox"]').checked;
        const tierBadge = item.querySelector('.tier-badge');
        const tier = tierBadge ? parseInt(tierBadge.textContent.match(/\d+/)[0]) : 4;
        
        priorities.push({ name, search, enabled, tier });
    });
    
    return priorities;
}

// Load supported sources (called from main.js)
async function loadSupportedSources() {
    // No longer needed - sources are loaded as part of priority list
    console.log('Sources loaded via populateAllSearchableSources()');
}
