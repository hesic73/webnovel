document.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowLeft') {
        const previousChapterLink = document.querySelector('#previous-chapter');
        if (previousChapterLink && !previousChapterLink.hasAttribute('disabled')) {
            window.location.href = previousChapterLink.href;
        }
    } else if (event.key === 'ArrowRight') {
        const nextChapterLink = document.querySelector('#next-chapter');
        if (nextChapterLink && !nextChapterLink.hasAttribute('disabled')) {
            window.location.href = nextChapterLink.href;
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login_form/';
        return;
    }
});

/**
 * 
 * @param {number} novelId 
 * @param {number} chapterId 
 */
function addBookmark(novelId, chapterId) {

    console.log('Bookmark button clicked');  // Log to confirm the function is called
    console.log('Novel ID:', novelId);
    console.log('Chapter ID:', chapterId);

    const token = localStorage.getItem('access_token');
    fetch('/api/bookmark/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            novel_id: novelId,
            chapter_id: chapterId
        })
    })
        .then(response => {
            if (response.ok) {
                alert('书签已更新');
            } else {
                throw new Error('Failed to update bookmark');
            }
        })
        .catch(error => {
            console.error('Error updating bookmark:', error);
            alert('更新书签时出错');
        });
}
