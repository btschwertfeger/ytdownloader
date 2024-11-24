# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# GitHub: https://github.com/btschwertfeger
#

from pathlib import Path
from typing import Any

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from yt_dlp import YoutubeDL


class DownloaderThread(QThread):
    """Thread to download a YouTube video or audio"""

    progress = Signal(str, str)  # (status, item)
    completed = Signal(str)

    def __init__(
        self: "DownloaderThread",
        url: str,
        folder: str,
        mode: str,
        item: str,
    ) -> None:
        super().__init__()
        self.url = url
        self.folder = folder
        self.mode = mode
        self.item = item

    def run(self: "DownloaderThread") -> None:
        """Download the video or audio"""
        try:
            ydl_opts: dict[str, Any] = {
                "outtmpl": str(Path(self.folder) / "%(title)s.%(ext)s"),
            }
            if self.mode == "audio":  # noqa: PLR2004
                ydl_opts.update(
                    {
                        "format": "bestaudio/best",
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            },
                        ],
                    },
                )
            else:  # Video mode
                ydl_opts["format"] = "best"

            with YoutubeDL(ydl_opts) as ydl:
                self.progress.emit("Downloading...", self.item)
                ydl.download([self.url])

            self.progress.emit("Complete", self.item)
            self.completed.emit(self.item)
        except Exception as e:  # noqa: BLE001
            self.progress.emit(f"Error: {e!s}", self.item)


class YouTubeDownloaderApp(QMainWindow):
    """Main application window"""

    def __init__(self: "YouTubeDownloaderApp") -> None:
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(300, 300, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Input Area
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit(placeholderText="YouTube URL")
        input_layout.addWidget(self.url_input)

        self.add_button = QPushButton("Add to List")
        self.add_button.clicked.connect(self.add_to_list)
        input_layout.addWidget(self.add_button)
        self.layout.addLayout(input_layout)

        # Download List
        self.download_list = QListWidget()
        self.layout.addWidget(self.download_list)

        # Folder Selection
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(placeholderText="Save to Folder")
        folder_layout.addWidget(self.folder_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        self.layout.addLayout(folder_layout)

        # Control Buttons
        control_layout = QHBoxLayout()

        self.download_video_button = QPushButton("Download Video")
        self.download_video_button.clicked.connect(lambda: self.download("video"))
        control_layout.addWidget(self.download_video_button)

        self.download_audio_button = QPushButton("Download Audio")
        self.download_audio_button.clicked.connect(lambda: self.download("audio"))
        control_layout.addWidget(self.download_audio_button)

        self.delete_button = QPushButton("Remove Selected")
        self.delete_button.clicked.connect(self.remove_selected)
        control_layout.addWidget(self.delete_button)

        self.layout.addLayout(control_layout)

        self.threads: dict = {}

    def browse_folder(self: "YouTubeDownloaderApp") -> None:
        """Open a dialog to select a folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def add_to_list(self: "YouTubeDownloaderApp") -> None:
        """Add the URL to the download list"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Error", "Please enter a YouTube URL")
            return

        # Check for duplicates
        for i in range(self.download_list.count()):
            if self.download_list.item(i).text().startswith(url):
                QMessageBox.warning(
                    self,
                    "Duplicate",
                    "This URL is already in the list.",
                )
                return

        self.download_list.addItem(url)
        self.url_input.clear()

    def remove_selected(self: "YouTubeDownloaderApp") -> None:
        """Remove the selected items from the list"""
        for item in self.download_list.selectedItems():
            self.download_list.takeItem(self.download_list.row(item))

    def log_status(self: "YouTubeDownloaderApp", message: str, item: str) -> None:
        """Update the status of an item in the list"""
        for i in range(self.download_list.count()):
            list_item = self.download_list.item(i)
            if list_item.text().startswith(item):  # Match only the base URL
                list_item.setText(f"{item} - {message}")
                break

    def download(self: "YouTubeDownloaderApp", mode: str) -> None:
        """Download the selected items in the list"""
        folder = self.folder_input.text().strip()
        if not folder:
            QMessageBox.critical(self, "Error", "Please select a folder")
            return

        for i in range(self.download_list.count()):
            item = self.download_list.item(i).text()
            # if "Error" in item:
            #     continue

            url = item.split(" - ")[0]  # Strip any status text
            self.log_status("Queued", url)

            thread = DownloaderThread(url, folder, mode, url)
            thread.progress.connect(self.log_status)

            # FIXME: if url was added twice, this may terminate the program
            thread.completed.connect(lambda x: self.threads.pop(x, None))
            self.threads[url] = thread
            thread.start()


def run() -> None:
    """Run the application"""

    app = QApplication([])
    window = YouTubeDownloaderApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    run()
