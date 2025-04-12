// Main application JavaScript file

// Global variables
let currentPath = "";
let currentView = "grid";
let isDarkMode = localStorage.getItem('darkMode') === 'true';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Apply dark mode if saved
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        document.getElementById('toggleTheme').innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Initial file fetch
    fetchFiles();
    calculateStorage();
    
    // Setup event listeners
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // Toggle view
    document.getElementById('toggleView').addEventListener('click', function() {
        const fileList = document.getElementById('file-list');
        if (currentView === 'grid') {
            fileList.classList.remove('grid-view');
            fileList.classList.add('list-view');
            this.innerHTML = '<i class="fas fa-th"></i>';
            currentView = 'list';
        } else {
            fileList.classList.remove('list-view');
            fileList.classList.add('grid-view');
            this.innerHTML = '<i class="fas fa-th-list"></i>';
            currentView = 'grid';
        }
    });

    // Toggle dark mode
    document.getElementById('toggleTheme').addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        this.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    // File upload
    document.getElementById('fileInput').addEventListener('change', function() {
        if (this.files.length > 0) {
            const formData = new FormData();
            for (let file of this.files) {
                formData.append("file", file);
            }
            formData.append("current_path", currentPath);
            fetch("/upload", {
                method: "POST",
                body: formData
            }).then(() => {
                fetchFiles(currentPath);
                this.value = "";
                calculateStorage();
            });
        }
    });

    // Search functionality
    document.getElementById('searchInput').addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const items = document.querySelectorAll('.item');
        
        items.forEach(item => {
            const fileName = item.querySelector('a').textContent.toLowerCase();
            if (fileName.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });

    // Close preview
    document.getElementById('close-preview').addEventListener('click', function() {
        document.getElementById('file-preview').style.display = 'none';
    });

    // Create folder
    document.getElementById('createFolder').addEventListener('click', function() {
        const folderName = prompt('Enter folder name:');
        if (folderName) {
            fetch('/create-folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: currentPath,
                    name: folderName
                })
            }).then(() => {
                fetchFiles(currentPath);
            });
        }
    });

    // Sort files
    document.getElementById('sortFiles').addEventListener('click', function() {
        const items = Array.from(document.querySelectorAll('.item'));
        const container = document.getElementById('file-list');
        
        items.sort((a, b) => {
            const aIsDir = a.querySelector('i').classList.contains('fa-folder');
            const bIsDir = b.querySelector('i').classList.contains('fa-folder');
            
            if (aIsDir && !bIsDir) return -1;
            if (!aIsDir && bIsDir) return 1;
            
            return a.querySelector('a').textContent.localeCompare(b.querySelector('a').textContent);
        });
        
        container.innerHTML = '';
        items.forEach(item => container.appendChild(item));
    });
}