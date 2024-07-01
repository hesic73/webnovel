document.addEventListener('DOMContentLoaded', () => {
    const novelItems = document.querySelectorAll('.novel-item');

    novelItems.forEach(item => {
        item.addEventListener('click', () => {
            const novelId = item.getAttribute('data-id');
            window.location.href = `/novel/${novelId}/`;
        });
    });
});
