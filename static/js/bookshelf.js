document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login_form.html';
        return;
    }

    fetch('/api/bookshelf/', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(error => {
                    throw new Error(error.detail || 'Unknown error');
                });
            }
            return response.json();
        })
        .then(data => {

            const title = document.getElementById('bookshelf-title');
            title.textContent = `${data.username}的书架`;

            const table = document.getElementById('bookshelf-table');
            table.innerHTML = '';

            data.entries.forEach(entry => {
                const row = document.createElement('tr');
                const chapterLink = entry.bookmarked_chapter
                    ? `<a class="custom-link-chapter" href="/novel/${entry.novel_id}/${entry.bookmarked_chapter.id}.html">${entry.bookmarked_chapter.title}</a>`
                    : '';


                const latestChapterLink = entry.latest_chapter
                    ? `<a class="custom-link-chapter" href="/novel/${entry.novel_id}/${entry.latest_chapter.id}.html">${entry.latest_chapter.title}</a>`
                    : '';

                row.innerHTML = `
                <td><a class="custom-link-chapter" href="/novel/${entry.novel_id}/">${entry.title}</a></td>
                <td><a class="custom-link-chapter" href="/author/${entry.author.id}/">${entry.author.name}</td>
                <td>${latestChapterLink}</td>
                <td>${chapterLink}</td>
                <td><button class="custom-link-chapter" onclick="removeFromBookshelf(${entry.novel_id})"><i class="fa-solid fa-trash-can"></i></button></td>
            `;
                table.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching bookshelf data:', error);
            const table = document.getElementById('bookshelf-table');
            table.innerHTML = `<tr><td colspan="5">加载失败，请稍后重试。错误详情: ${error.message}</td></tr>`;
        });
});

/**
 * 
 * @param {number} novel_id 
 */
function removeFromBookshelf(novel_id) {
    const token = localStorage.getItem('access_token');
    fetch(`/api/bookshelf/${novel_id}/`, {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                location.reload(); // Refresh the page to update the bookshelf
            } else {
                console.error('Error removing book from bookshelf');
            }
        })
        .catch(error => {
            console.error('Error removing book from bookshelf:', error);
        });
}
