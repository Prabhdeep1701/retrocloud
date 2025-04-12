// Special views like recent, starred, etc.

// Show recent files
function showRecent() {
    fetch('/recent')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("file-list");
            container.innerHTML = '<h2 style="margin-bottom: 20px; border-bottom: 3px solid var(--border-color); padding-bottom: 10px;">Recent Files</h2>';
            
            data.files.forEach(item => {
                addFileOrFolderItem(container, item);
            });
            
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            document.querySelector('.nav-item:nth-child(2)').classList.add('active');
        });
}

// Show starred files
function showStarred() {
    // This would be implemented with backend support
    alert('Starred files feature coming soon!');
}

// Show trash
function showTrash() {
    // This would be implemented with backend support
    alert('Trash feature coming soon!');
}