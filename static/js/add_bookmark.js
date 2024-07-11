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