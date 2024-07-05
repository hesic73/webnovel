#!/usr/bin/env python3

from app.enums import Genre
from app.database.chapter import create_chapter
from app.database.novel import create_novel
from app.spiders.biquge1 import get_novel_data, get_chapter_content
from app.database import get_db_sync
import sys
from typing import Callable
import os
import time
from sqlalchemy.orm import Session

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QComboBox, QPushButton, QProgressBar, QMessageBox


def add_novel_to_database_biquge(db: Session, novel_url: str, genre: Genre, on_chapter_update: Callable[[int], None] = None):
    novel_data = get_novel_data(novel_url)

    # Create novel entry
    novel = create_novel(
        db=db,
        title=novel_data['title'],
        author_name=novel_data['author'],
        genre=genre,
        description=novel_data['intro']
    )

    # Add chapters
    for i, chapter in enumerate(novel_data['chapters']):
        print(chapter)
        chapter_content = get_chapter_content(chapter[1])
        create_chapter(
            db=db,
            novel_id=novel.id,
            chapter_number=novel_data['chapters'].index(chapter) + 1,
            title=chapter[0],
            content=chapter_content
        )

        if on_chapter_update:
            on_chapter_update(i + 1)

        # Sleep between requests to avoid overloading the server
        time.sleep(0.2)

    return novel


class Worker(QThread):
    progress = pyqtSignal(int)
    max_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, url: str, genre: Genre):
        super().__init__()
        self.url = url
        self.genre = genre

    def run(self):
        db = next(get_db_sync())  # Get synchronous DB session
        try:
            novel_data = get_novel_data(self.url)
            self.max_progress.emit(len(novel_data['chapters']))

            add_novel_to_database_biquge(
                db=db,
                novel_url=self.url,
                genre=self.genre,
                on_chapter_update=self.progress.emit
            )
        finally:
            db.close()
            self.finished.emit()


class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("从笔趣阁爬取小说")

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

        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            return

        QMessageBox.information(self, "Input Information",
                                f"URL: {url}\nSelected Genre: {genre.value}")
        

        self.start_button.setDisabled(True)

        self.worker = Worker(url, genre)
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
