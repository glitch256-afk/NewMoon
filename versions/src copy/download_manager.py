import os
import subprocess
import sys
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QWidget, QLabel, QProgressBar, QPushButton, QFileDialog
)
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest


class DownloadItemWidget(QWidget):
    def __init__(self, download_item: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)
        self.download_item = download_item

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(8, 8, 8, 8)

        # File name display
        filename = self.download_item.downloadFileName() or "Unknown File"
        self.info_label = QLabel(f"<b>{filename}</b>")
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(14)

        # Controls Layout
        controls_layout = QHBoxLayout()
        self.status_label = QLabel("Starting...")
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedSize(60, 24)
        self.cancel_btn.clicked.connect(self.cancel_download)

        self.open_folder_btn = QPushButton("Show in Folder")
        self.open_folder_btn.setFixedSize(100, 24)
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_folder)

        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.cancel_btn)
        controls_layout.addWidget(self.open_folder_btn)

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addLayout(controls_layout)
        self.setLayout(self.layout)

        # Wire QtWebEngine Download Signals
        self.download_item.receivedBytesChanged.connect(self.update_progress)
        self.download_item.stateChanged.connect(self.on_state_changed)

    def update_progress(self):
        received = self.download_item.receivedBytes()
        total = self.download_item.totalBytes()

        if total > 0:
            percent = int((received / total) * 100)
            self.progress_bar.setValue(percent)
            mb_rec = received / (1024 * 1024)
            mb_tot = total / (1024 * 1024)
            self.status_label.setText(f"{mb_rec:.1f} MB / {mb_tot:.1f} MB ({percent}%)")
        else:
            self.progress_bar.setRange(0, 0)
            mb_rec = received / (1024 * 1024)
            self.status_label.setText(f"{mb_rec:.1f} MB downloaded")

    def on_state_changed(self, state):
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.status_label.setText("Completed")
            self.cancel_btn.setEnabled(False)
            self.open_folder_btn.setEnabled(True)
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self.status_label.setText("Cancelled")
            self.cancel_btn.setEnabled(False)
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            self.status_label.setText("Interrupted")
            self.cancel_btn.setEnabled(False)

    def cancel_download(self):
        self.download_item.cancel()

    def open_folder(self):
        folder = self.download_item.downloadDirectory()
        if os.path.exists(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])


class DownloadManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads Manager")
        self.resize(550, 380)

        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def add_download(self, download_item: QWebEngineDownloadRequest):
        item = QListWidgetItem(self.list_widget)
        widget = DownloadItemWidget(download_item, self)
        
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        
        self.show()
        self.raise_()