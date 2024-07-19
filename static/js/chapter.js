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
    const savedFontSize = localStorage.getItem('fontSize');
    if (savedFontSize) {
        const chapterContent = document.getElementById('chapter-content');
        chapterContent.classList.remove('is-size-1', 'is-size-2', 'is-size-3', 'is-size-4', 'is-size-5', 'is-size-6');
        chapterContent.classList.add(savedFontSize);
        document.getElementById('fonttype').value = savedFontSize;
    }
});


function changeContentFontSize(selectElement) {
    var selectedClass = selectElement.value;
    var chapterContent = document.getElementById('chapter-content');

    // Remove existing size classes
    chapterContent.classList.remove('is-size-1', 'is-size-2', 'is-size-3', 'is-size-4', 'is-size-5', 'is-size-6');

    // Add the selected size class
    chapterContent.classList.add(selectedClass);

    localStorage.setItem('fontSize', selectedClass);
}