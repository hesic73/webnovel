async function loginUser() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            password: password
        }),
    });

    const notification = document.getElementById('notification');

    if (response.ok) {
        const result = await response.json();
        localStorage.setItem('access_token', result.access_token); // Save token locally
        window.location.href = '/';
    } else {
        const result = await response.json();
        notification.classList.remove('is-hidden', 'is-success');
        notification.classList.add('is-danger');
        notification.textContent = '登录失败: ' + result.detail;
    }
}
