#!/usr/bin/env python3

from app.enums import Genre, ScraperSource
from app.database.session import SessionLocal
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QComboBox, QPushButton, QProgressBar, QMessageBox


from app.utils.scraper_utils import make_scraper_function


class Worker(QThread):
    progress = pyqtSignal(int)
    max_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, url: str, genre: Genre, scraper_source: ScraperSource):
        super().__init__()
        self.url = url
        self.genre = genre

        self.add_novel_to_database = make_scraper_function(scraper_source)

    def run(self):
        db = SessionLocal()
        try:
            self.add_novel_to_database(
                db=db,
                novel_url=self.url,
                genre=self.genre,
                post_get_novel_data=lambda novel_data: self.max_progress.emit(
                    len(novel_data['chapters'])),
                on_chapter_update=self.progress.emit
            )
        finally:
            db.close()
            self.finished.emit()


class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("爬取小说")

        # Main widget
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Layout
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        # Horizontal layout for URL LineEdit and Genre ComboBox
        self.horizontal_layout = QHBoxLayout()

        # URL LineEdit
        self.url_line_edit = QLineEdit(self)
        self.url_line_edit.setPlaceholderText("Enter URL")
        self.horizontal_layout.addWidget(self.url_line_edit)

        # Genre ComboBox
        self.genre_combo_box = QComboBox(self)
        self.genre_combo_box.addItems(
            [g.value for g in Genre])
        self.genre_combo_box.setCurrentIndex(0)

        self.horizontal_layout.addWidget(self.genre_combo_box)

        self.source_combo_box = QComboBox(self)
        self.source_combo_box.addItems(
            [s.name for s in ScraperSource])
        self.source_combo_box.setCurrentIndex(0)

        self._source_index_to_enum = {
            i: s for i, s in enumerate(ScraperSource)}

        self.horizontal_layout.addWidget(self.source_combo_box)

        self.main_layout.addLayout(self.horizontal_layout)

        # Start Button
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.main_layout.addWidget(self.start_button)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.main_layout.addWidget(self.progress_bar)

    def on_start_button_clicked(self):
        url = self.url_line_edit.text()
        genre = Genre(self.genre_combo_box.currentText())
        source = self._source_index_to_enum[self.source_combo_box.currentIndex(
        )]

        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            return

        QMessageBox.information(self, "Input Information",
                                f"URL: {url}\nSelected Genre: {genre.value}")

        self.start_button.setDisabled(True)

        self.worker = Worker(url, genre, scraper_source=source)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.max_progress.connect(self.set_max_progress)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def set_max_progress(self, max_value):
        self.progress_bar.setRange(0, max_value)

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def on_worker_finished(self):
        self.start_button.setDisabled(False)  # Re-enable start button
        QMessageBox.information(
            self, "Task Completed", "The task has been completed successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    gui.show()
    sys.exit(app.exec_())
