document.getElementById('scrape-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const url = document.getElementById('url').value;
    const source = parseInt(document.getElementById('source').value);
    const genre = document.getElementById('genre').value;

    const scrapeData = {
        url: url,
        source: source,
        genre: genre
    };

    const token = localStorage.getItem('access_token');

    if (!token) {
        const messageElement = document.getElementById('message');
        messageElement.className = 'notification is-danger';
        messageElement.textContent = '请先登录';
        messageElement.classList.remove('is-hidden');
    }

    try {
        const response = await fetch('/internal/scrape/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            },
            body: JSON.stringify(scrapeData)
        });

        const result = await response.json();

        const messageElement = document.getElementById('message');
        if (response.ok) {
            messageElement.className = 'notification is-success';
            messageElement.textContent = result.message;
        } else {
            messageElement.className = 'notification is-danger';
            messageElement.textContent = 'Error: ' + result.detail;
        }
        messageElement.classList.remove('is-hidden');
    } catch (error) {
        const messageElement = document.getElementById('message');
        messageElement.className = 'notification is-danger';
        messageElement.textContent = 'Error: ' + error.message;
        messageElement.classList.remove('is-hidden');
    }
});