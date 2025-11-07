// Main JavaScript file for WeBook

document.addEventListener('DOMContentLoaded', function() {
    console.log('WeBook initialized');
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });
});

// Helper function for AJAX requests
function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => response.json())
        .catch(error => {
            console.error('API request failed:', error);
            throw error;
        });
}

// Bookmark toggle function
function toggleBookmark(bookId) {
    const isBookmarked = document.querySelector(`[data-book-id="${bookId}"]`)
        .classList.contains('bookmarked');
    
    const method = isBookmarked ? 'DELETE' : 'POST';
    const url = `/books/${bookId}/bookmark`;
    
    apiRequest(url, method)
        .then(data => {
            console.log(data.message);
            location.reload();
        })
        .catch(error => {
            alert('Failed to update bookmark');
        });
}

// Rating function
function rateBook(bookId, score) {
    const url = `/books/${bookId}/rating`;
    
    apiRequest(url, 'POST', { score: score })
        .then(data => {
            console.log(data.message);
            location.reload();
        })
        .catch(error => {
            alert('Failed to submit rating');
        });
}

// Star rating display
function displayStarRating(containerId, rating, interactive = false, bookId = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('span');
        star.className = i <= rating ? 'star filled' : 'star';
        star.innerHTML = '★';
        
        if (interactive && bookId) {
            star.style.cursor = 'pointer';
            star.addEventListener('click', () => rateBook(bookId, i));
        }
        
        container.appendChild(star);
    }
}
