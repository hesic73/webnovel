document.addEventListener("DOMContentLoaded", function () {
    function adjustEmptyCells() {
        const container = document.getElementById('chapters-container');

        if (!container) {
            return;
        }

        const cells = container.getElementsByClassName('cell');
        const containerWidth = container.offsetWidth;

        let itemsPerRow;
        if (containerWidth < 768) {
            itemsPerRow = 1;
        } else if (containerWidth < 1024) {
            itemsPerRow = 3;
        } else {
            itemsPerRow = 4;
        }

        const remainder = cells.length % itemsPerRow;
        const emptyCellsNeeded = (remainder === 0) ? 0 : itemsPerRow - remainder;

        // Remove existing empty cells
        while (container.getElementsByClassName('empty-cell').length > 0) {
            container.removeChild(container.getElementsByClassName('empty-cell')[0]);
        }

        // Add new empty cells
        for (let i = 0; i < emptyCellsNeeded; i++) {
            const emptyCell = document.createElement('dd');
            emptyCell.className = 'cell empty-cell';
            container.appendChild(emptyCell);
        }
    }

    // Initial adjustment
    adjustEmptyCells();

    // Adjust on window resize
    window.addEventListener('resize', adjustEmptyCells);
});