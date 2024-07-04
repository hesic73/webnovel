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