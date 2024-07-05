document.addEventListener("DOMContentLoaded", function () {
    // Check if the token exists in localStorage
    const token = localStorage.getItem('access_token');
    const navbarButtons = document.getElementById('navbar-buttons');

    if (token) {
        navbarButtons.innerHTML = `
            <a class="button is-light" href="/bookshelf/">
                书架
            </a>
            <a class="button is-light" href="#" id="logout-button">
                登出
            </a>
        `;

        // Add logout functionality
        document.getElementById('logout-button').addEventListener('click', function () {
            localStorage.removeItem('access_token');
            window.location.reload(); // Refresh the page to update the navbar
        });
    }
});