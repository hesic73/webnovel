document.addEventListener("DOMContentLoaded", function () {
    // Check if the token exists in localStorage
    const token = localStorage.getItem('access_token');
    const navbarButtons = document.getElementById('user-panel');

    if (token) {
        navbarButtons.innerHTML = `
        <a href="/bookshelf/" class="custom-link-normal">书架</a>
        <a id="logout-button" href="#" class="custom-link-normal">登出</a>
        `;

        // Add logout functionality
        document.getElementById('logout-button').addEventListener('click', function () {
            localStorage.removeItem('access_token');
            window.location.reload(); // Refresh the page to update the navbar
        });
    }
});


function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function scrollToBottom() {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}


/**
 * 
 * @param {number} novelId 
 * @param {number} chapterId 
 */
function addBookmark(novelId, chapterId = null) {

    console.log('Bookmark button clicked');  // Log to confirm the function is called
    console.log('Novel ID:', novelId);
    console.log('Chapter ID:', chapterId);

    const token = localStorage.getItem('access_token');
    const requestBody = {
        novel_id: novelId,
    };
    if (chapterId !== null) {
        requestBody.chapter_id = chapterId;
    }

    fetch('/api/bookmark/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
        .then(response => {
            if (response.ok) {
                alert('书签已更新');
            } else {
                return response.json().then(error => {
                    throw new Error(error.detail || 'Unknown error');
                });
            }
        })
        .catch(error => {
            console.error('Error updating bookmark:', error.message);
            alert('更新书签时出错: ' + error.message);
        });

}