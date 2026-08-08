from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMenu


class BookmarksBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedHeight(26)
        self.setObjectName("BookmarksBar")

        self.bm_layout = QHBoxLayout()
        self.bm_layout.setContentsMargins(4, 1, 4, 1)
        self.bm_layout.setSpacing(3)
        self.bm_layout.addStretch()
        self.setLayout(self.bm_layout)

        self.apply_styles()
        self.load_defaults()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget#BookmarksBar {{
                background-color: {self.main_window.bg_color};
                border-bottom: 1px solid #333333;
            }}
            QPushButton {{
                font-size: 11px;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 2px 8px;
                background: transparent;
                color: {self.main_window.text_color};
                max-height: 22px;
            }}
            QPushButton:hover {{
                background-color: {self.main_window.accent_hover};
                border: 1px solid {self.main_window.accent_color};
            }}
        """)

    def load_defaults(self):
        default_bookmarks = [
            ("🔍 DuckDuckGo", "https://duckduckgo.com"),
            ("🔖 Pale Moon", "https://palemoon.org"),
            ("📚 Wikipedia", "https://wikipedia.org"),
            ("🏛️ Archive.org", "https://archive.org")
        ]
        for name, url in default_bookmarks:
            self.add_bookmark_btn(name, url)

    def add_bookmark_btn(self, name, url):
        btn = QPushButton(name)
        btn.setToolTip(url)
        btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        btn.clicked.connect(
            lambda: self.main_window.current_browser().setUrl(QUrl(url)) 
            if self.main_window.current_browser() else None
        )
        btn.customContextMenuRequested.connect(
            lambda pos, b=btn: self.show_context_menu(pos, b)
        )
        
        count = self.bm_layout.count()
        if count > 0:
            self.bm_layout.insertWidget(count - 1, btn)
        else:
            self.bm_layout.addWidget(btn)

    def show_context_menu(self, pos, btn):
        menu = QMenu(self)
        delete_action = QAction("Remove Bookmark", self)
        delete_action.triggered.connect(lambda: self.remove_bookmark(btn))
        menu.addAction(delete_action)
        menu.exec(btn.mapToGlobal(pos))

    def remove_bookmark(self, btn):
        self.bm_layout.removeWidget(btn)
        btn.deleteLater()
        self.main_window.status.showMessage("Bookmark removed", 3000)