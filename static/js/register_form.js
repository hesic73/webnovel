
async function registerUser() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        }),
    });

    const notification = document.getElementById('notification');

    if (response.ok) {
        notification.classList.remove('is-hidden', 'is-danger');
        notification.classList.add('is-success');
        notification.textContent = '注册成功!';
        window.location.href = '/login_form/';
    } else {
        const result = await response.json();
        notification.classList.remove('is-hidden', 'is-success');
        notification.classList.add('is-danger');
        notification.textContent = '注册失败: ' + result.detail;
    }
}
