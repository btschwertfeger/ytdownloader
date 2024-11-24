# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# GitHub: https://github.com/btschwertfeger
#

import os
import tempfile

import pytest

from ytdownloader.app import YouTubeDownloaderApp


@pytest.fixture
def app(qtbot):  # noqa: ANN201
    test_app = YouTubeDownloaderApp()
    qtbot.addWidget(test_app)
    return test_app


def test_download_audio(app, qtbot) -> None:
    """Test downloading audio"""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    with tempfile.TemporaryDirectory() as test_folder:
        # Simulate user input
        app.url_input.setText(test_url)
        app.folder_input.setText(test_folder)
        app.add_to_list()
        app.download("audio")

        # Wait for the download to complete
        qtbot.waitUntil(lambda: not app.threads, timeout=60000)  # 60 seconds timeout

        # Verify that the file exists
        downloaded_files = os.listdir(test_folder)
        assert any(
            file.endswith(".mp3") for file in downloaded_files
        ), "Downloaded file not found"


def test_download_video(app, qtbot) -> None:
    """Test downloading video"""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    with tempfile.TemporaryDirectory() as test_folder:
        # Simulate user input
        app.url_input.setText(test_url)
        app.folder_input.setText(test_folder)
        app.add_to_list()
        app.download("video")

        # Wait for the download to complete
        qtbot.waitUntil(lambda: not app.threads, timeout=60000)  # 60 seconds timeout

        # Verify that the file exists
        downloaded_files = os.listdir(test_folder)
        assert any(
            file.endswith(".mp4") for file in downloaded_files
        ), "Downloaded video file not found"
