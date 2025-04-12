// File operations

// Calculate storage
function calculateStorage() {
    fetch('/storage-info')
        .then(response => response.json())
        .then(data => {
            const usedPercent = (data.used / data.total) * 100;
            document.getElementById('storageUsed').style.width = `${usedPercent}%`;
            document.getElementById('storageText').textContent = 
                `${formatBytes(data.used)} / ${formatBytes(data.total)} used`;
        });
}

// Format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Fetch files function
function fetchFiles(path = "") {
    fetch(`/browse?path=${encodeURIComponent(path)}`)
        .then(response => response.json())
        .then(data => {
            currentPath = data.current_path;
            
            // Update path navigation
            updatePathNavigation(currentPath);
            
            // Update file list
            const container = document.getElementById("file-list");
            container.innerHTML = '';
            
            // Add parent directory link if not at root
            if (currentPath && currentPath !== '.') {
                addParentDirectoryLink(container, currentPath);
            }
            
            // Add files and folders
            data.contents.forEach(item => {
                addFileOrFolderItem(container, item);
            });
        })
        .catch(error => {
            console.error("Error fetching files:", error);
            alert("Error loading files. Please try again.");
        });
}

// Update path navigation
function updatePathNavigation(path) {
    const pathNav = document.getElementById("path-nav");
    let pathParts = path.split('/').filter(part => part);
    let pathHtml = `<a href="#" onclick="fetchFiles('')">My Drive</a>`;
    let currentPathBuild = "";
    
    for (let i = 0; i < pathParts.length; i++) {
        currentPathBuild += pathParts[i] + "/";
        pathHtml += ` / <a href="#" onclick="fetchFiles('${currentPathBuild}')">${pathParts[i]}</a>`;
    }
    
    pathNav.innerHTML = pathHtml;
}

// Add parent directory link
function addParentDirectoryLink(container, path) {
    const parentPath = path.split('/').slice(0, -1).join('/');
    const parentEl = document.createElement("div");
    parentEl.className = "item";
    parentEl.innerHTML = `
        <div class="item-icon"><i class="fas fa-arrow-up"></i></div>
        <div class="item-details">
            <a href="#" onclick="fetchFiles('${parentPath}')">Parent Directory</a>
        </div>
    `;
    container.appendChild(parentEl);
}

// Add file or folder item
function addFileOrFolderItem(container, item) {
    const el = document.createElement("div");
    el.className = item.is_dir ? "item folder" : "item";
    
    // Determine icon based on file type
    let icon = '';
    if (item.is_dir) {
        icon = '<i class="fas fa-folder"></i>';
    } else {
        const ext = item.name.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
            icon = '<i class="fas fa-image"></i>';
        } else if (['mp4', 'webm', 'avi', 'mov'].includes(ext)) {
            icon = '<i class="fas fa-video"></i>';
        } else if (['mp3', 'wav', 'ogg'].includes(ext)) {
            icon = '<i class="fas fa-music"></i>';
        } else if (['pdf'].includes(ext)) {
            icon = '<i class="fas fa-file-pdf"></i>';
        } else if (['doc', 'docx'].includes(ext)) {
            icon = '<i class="fas fa-file-word"></i>';
        } else if (['xls', 'xlsx'].includes(ext)) {
            icon = '<i class="fas fa-file-excel"></i>';
        } else if (['ppt', 'pptx'].includes(ext)) {
            icon = '<i class="fas fa-file-powerpoint"></i>';
        } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
            icon = '<i class="fas fa-file-archive"></i>';
        } else if (['txt', 'md'].includes(ext)) {
            icon = '<i class="fas fa-file-alt"></i>';
        } else if (['html', 'css', 'js', 'py', 'java', 'c', 'cpp'].includes(ext)) {
            icon = '<i class="fas fa-file-code"></i>';
        } else {
            icon = '<i class="fas fa-file"></i>';
        }
    }
    
    // Create item HTML
    el.innerHTML = `
        <div class="item-icon">${icon}</div>
        <div class="item-details">
            <a href="#" onclick="${item.is_dir ? `fetchFiles('${item.path}')` : `previewFile('${item.path}', '${item.name}')`}">${item.name}</a>
            <div class="item-actions">
                <button onclick="toggleStar(this, event)" title="Star"><i class="far fa-star"></i></button>
                ${!item.is_dir ? `<button onclick="deleteFile('${item.path}', event)" title="Delete"><i class="fas fa-trash"></i></button>` : ''}
            </div>
        </div>
    `;
    
    container.appendChild(el);
}

// Preview file
function previewFile(path, name) {
    const preview = document.getElementById('file-preview');
    const previewBody = document.getElementById('preview-body');
    const previewFilename = document.getElementById('preview-filename');
    
    previewFilename.textContent = name;
    
    const ext = name.split('.').pop().toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
        previewBody.innerHTML = `<img src="/download?path=${path}" alt="${name}">`;
    } else if (['mp4', 'webm'].includes(ext)) {
        previewBody.innerHTML = `
            <video controls style="max-width: 100%;">
                <source src="/download?path=${path}" type="video/${ext}">
                Your browser does not support the video tag.
            </video>
        `;
    } else if (['mp3', 'wav', 'ogg'].includes(ext)) {
        previewBody.innerHTML = `
            <audio controls>
                <source src="/download?path=${path}" type="audio/${ext}">
                Your browser does not support the audio tag.
            </audio>
        `;
    } else if (['txt', 'md', 'html', 'css', 'js', 'py', 'java', 'c', 'cpp'].includes(ext)) {
        fetch(`/download?path=${path}`)
            .then(response => response.text())
            .then(text => {
                previewBody.innerHTML = `<pre style="text-align: left; max-height: 60vh; overflow: auto; background: var(--bg-secondary); padding: 15px; color: var(--text-primary); border: 3px solid var(--border-color);">${text}</pre>`;
            });
    } else {
        previewBody.innerHTML = `
            <div style="padding: 20px;">
                <p>No preview available for this file type</p>
                <a href="/download?path=${path}" class="download-btn">Download</a>
            </div>
        `;
    }
    
    preview.style.display = 'block';
}

// Toggle star
function toggleStar(btn, event) {
    event.stopPropagation();
    const icon = btn.querySelector('i');
    if (icon.classList.contains('far')) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        icon.style.color = '#ffde59';
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        icon.style.color = '';
    }
}

// Delete file function
function deleteFile(path, event) {
    if (event) event.stopPropagation();
    if (confirm('Are you sure you want to delete this file?')) {
        fetch(`/delete?path=${path}`, {
            method: 'DELETE'
        }).then(response => {
            if (response.ok) {
                fetchFiles(currentPath);
                calculateStorage();
            }
        });
    }
}