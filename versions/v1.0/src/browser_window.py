import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QKeySequence, QPalette, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLineEdit, QPushButton, QStatusBar, QProgressBar, 
    QTabWidget, QToolButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile

from src.interceptor import AdBlockInterceptor
from src.dialogs import PreferencesDialog
from src.bookmarks import BookmarksBar
from src.find_bar import FindBar


class PaleMoonChromiumBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NewMoon Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.home_url = "https://duckduckgo.com"
        self.web_view_padding = 16
        self.search_engine = "DuckDuckGo"
        self.search_engines = {
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Google": "https://www.google.com/search?q=",
            "Bing": "https://www.bing.com/search?q=",
            "Brave": "https://search.brave.com/search?q="
        }

        # System theme colors
        palette = self.palette()
        self.bg_color = palette.color(QPalette.ColorRole.Window).name()
        self.base_color = palette.color(QPalette.ColorRole.Base).name()
        self.text_color = palette.color(QPalette.ColorRole.WindowText).name()
        self.accent_color = palette.color(QPalette.ColorRole.Highlight).name()
        accent_qcolor = palette.color(QPalette.ColorRole.Highlight)
        self.accent_hover = f"rgba({accent_qcolor.red()}, {accent_qcolor.green()}, {accent_qcolor.blue()}, 0.3)"

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Global Interceptor
        self.ad_interceptor = AdBlockInterceptor(self)
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.ad_interceptor)

        # Build UI Elements
        self.create_menu_bar()
        self.create_toolbar()
        
        self.bookmarks_bar = BookmarksBar(self)
        self.main_layout.addWidget(self.bookmarks_bar)

        self.create_tab_widget()

        self.find_bar = FindBar(self)
        self.main_layout.addWidget(self.find_bar)

        self.create_status_bar()

        self.add_new_tab(QUrl(self.home_url), "DuckDuckGo")

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def create_tab_widget(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        self.add_tab_button = QToolButton()
        self.add_tab_button.setText("+")
        self.add_tab_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_tab_button.setFixedSize(28, 24)
        self.add_tab_button.clicked.connect(lambda: self.add_new_tab())
        self.tabs.setCornerWidget(self.add_tab_button, Qt.Corner.TopRightCorner)

        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 0px; }}
            QTabBar::tab {{
                background: {self.bg_color};
                color: {self.text_color};
                padding: 5px 12px;
                border: 1px solid transparent;
                font-size: 11px;
            }}
            QTabBar::tab:selected {{
                background: {self.base_color};
                border-top: 2px solid {self.accent_color};
            }}
            QTabBar::tab:hover {{ background: {self.accent_hover}; }}
            QToolButton {{
                background: transparent;
                color: {self.text_color};
                border: none;
                font-size: 16px;
                font-weight: bold;
                margin-right: 4px;
            }}
            QToolButton:hover {{
                background-color: {self.accent_hover};
                border-radius: 3px;
            }}
        """)
        self.main_layout.addWidget(self.tabs)

    def current_browser(self):
        wrapper = self.tabs.currentWidget()
        if wrapper:
            return wrapper.findChild(QWebEngineView)
        return None

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl(self.home_url)

        browser = QWebEngineView()
        browser.setUrl(qurl)

        padded_wrapper = QWidget()
        padded_wrapper.setStyleSheet(f"background-color: {self.bg_color};")
        wrapper_layout = QHBoxLayout()
        wrapper_layout.setContentsMargins(self.web_view_padding, 0, self.web_view_padding, 0)
        wrapper_layout.addWidget(browser)
        padded_wrapper.setLayout(wrapper_layout)
        
        index = self.tabs.addTab(padded_wrapper, label)
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda url, b=browser: self.on_url_changed(url, b))
        browser.titleChanged.connect(lambda title, b=browser: self.on_title_changed(title, b))
        browser.loadProgress.connect(lambda progress, b=browser: self.on_load_progress(progress, b))
        browser.loadFinished.connect(lambda success, b=browser: self.on_load_finished(success, b))
        browser.page().linkHovered.connect(lambda url: self.status.showMessage(url if url else "Done"))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def tab_changed(self, index):
        browser = self.current_browser()
        if browser:
            self.update_address_bar(browser.url())

    def on_url_changed(self, qurl, browser):
        if browser == self.current_browser():
            self.update_address_bar(qurl)

    def on_title_changed(self, title, browser):
        for i in range(self.tabs.count()):
            wrapper = self.tabs.widget(i)
            if wrapper and wrapper.findChild(QWebEngineView) == browser:
                short_title = title[:18] + "..." if len(title) > 18 else title
                self.tabs.setTabText(i, short_title)
                break

    def on_load_progress(self, progress, browser):
        if browser == self.current_browser() and progress < 100:
            self.progress_bar.show()
            self.progress_bar.setValue(progress)
            self.status.showMessage(f"Loading page... {progress}%")

    def on_load_finished(self, success, browser):
        if browser == self.current_browser():
            self.progress_bar.hide()
            self.status.showMessage("Done")

    def open_preferences(self):
        dialog = PreferencesDialog(self.home_url, self.web_view_padding, self.search_engine, self)
        if dialog.exec():
            settings = dialog.get_settings()
            self.home_url = settings["home_url"]
            self.web_view_padding = settings["padding"]
            self.search_engine = settings["engine"]
            self.search_bar.setPlaceholderText(f"Search {self.search_engine}...")

            for i in range(self.tabs.count()):
                wrapper = self.tabs.widget(i)
                if wrapper and wrapper.layout():
                    wrapper.layout().setContentsMargins(self.web_view_padding, 0, self.web_view_padding, 0)

            self.status.showMessage("Preferences updated", 3000)

    def create_menu_bar(self):
        menubar = self.menuBar()
        if sys.platform == "darwin":
            menubar.setNativeMenuBar(True)

        file_menu = menubar.addMenu("&File")
        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut(QKeySequence.StandardKey.AddTab)
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")
        find_action = QAction("Find in Page...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(lambda: self.find_bar.show_find_bar())
        edit_menu.addAction(find_action)

        pref_action = QAction("Preferences...", self)
        pref_action.setShortcut(QKeySequence.StandardKey.Preferences)
        pref_action.triggered.connect(self.open_preferences)
        edit_menu.addAction(pref_action)

        view_menu = menubar.addMenu("&View")
        toggle_nav = QAction("Toggle Navigation Bar", self, checkable=True)
        toggle_nav.setChecked(True)
        toggle_nav.triggered.connect(lambda: self.toolbar_widget.setVisible(toggle_nav.isChecked()))
        view_menu.addAction(toggle_nav)

        toggle_bm = QAction("Toggle Bookmarks Bar", self, checkable=True)
        toggle_bm.setChecked(True)
        toggle_bm.triggered.connect(lambda: self.bookmarks_bar.setVisible(toggle_bm.isChecked()))
        view_menu.addAction(toggle_bm)

        bm_menu = menubar.addMenu("&Bookmarks")
        add_bm_action = QAction("Bookmark This Page", self)
        add_bm_action.setShortcut(QKeySequence("Ctrl+D" if sys.platform != "darwin" else "Cmd+D"))
        add_bm_action.triggered.connect(self.add_bookmark)
        bm_menu.addAction(add_bm_action)

    def create_toolbar(self):
        self.toolbar_widget = QWidget()
        self.toolbar_widget.setFixedHeight(34)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(3, 3, 3, 3)
        nav_layout.setSpacing(3)

        self.toolbar_widget.setStyleSheet(f"""
            QWidget {{ font-size: 12px; background-color: {self.bg_color}; color: {self.text_color}; }}
            QPushButton {{ 
                padding: 0px; margin: 0px; max-height: 28px; min-height: 28px; font-size: 13px;
                border: 1px solid transparent; border-radius: 3px; background-color: transparent; color: {self.text_color};
            }}
            QPushButton:hover {{ background-color: {self.accent_hover}; border: 1px solid {self.accent_color}; }}
            QLineEdit {{ 
                padding: 2px 6px; margin: 0px; max-height: 26px; min-height: 26px; font-size: 12px;
                background-color: {self.base_color}; color: {self.text_color}; border: 1px solid #444444; border-radius: 3px;
            }}
            QLineEdit:focus {{ border: 1px solid {self.accent_color}; }}
        """)

        self.back_btn = QPushButton("◀")
        self.back_btn.setFixedSize(28, 28)
        self.back_btn.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setFixedSize(28, 28)
        self.forward_btn.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFixedSize(28, 28)
        self.refresh_btn.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)

        self.stop_btn = QPushButton("✖")
        self.stop_btn.setFixedSize(28, 28)
        self.stop_btn.clicked.connect(lambda: self.current_browser().stop() if self.current_browser() else None)

        self.home_btn = QPushButton("🏠")
        self.home_btn.setFixedSize(28, 28)
        self.home_btn.clicked.connect(lambda: self.current_browser().setUrl(QUrl(self.home_url)) if self.current_browser() else None)

        self.ad_block_btn = QPushButton("🛡️")
        self.ad_block_btn.setFixedSize(28, 28)
        self.ad_block_btn.setToolTip("Ad Blocker Enabled")
        self.ad_block_btn.clicked.connect(self.toggle_ad_blocker)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_url)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(f"Search {self.search_engine}...")
        self.search_bar.setMaximumWidth(180)
        self.search_bar.returnPressed.connect(self.execute_search)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)
        nav_layout.addWidget(self.stop_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.ad_block_btn)
        nav_layout.addWidget(self.address_bar, stretch=4)
        nav_layout.addWidget(self.search_bar, stretch=1)

        self.toolbar_widget.setLayout(nav_layout)
        self.main_layout.addWidget(self.toolbar_widget)

    def toggle_ad_blocker(self):
        self.ad_interceptor.enabled = not self.ad_interceptor.enabled
        if self.ad_interceptor.enabled:
            self.ad_block_btn.setText("🛡️")
            self.ad_block_btn.setToolTip("Ad Blocker Enabled")
            self.status.showMessage("Ad Blocker Enabled", 3000)
        else:
            self.ad_block_btn.setText("🛡️❌")
            self.ad_block_btn.setToolTip("Ad Blocker Disabled")
            self.status.showMessage("Ad Blocker Disabled", 3000)

    def add_bookmark(self):
        browser = self.current_browser()
        if browser:
            title = browser.title() or "Bookmark"
            url = browser.url().toString()
            display_title = f"🔖 {title[:15]}..." if len(title) > 15 else f"🔖 {title}"
            self.bookmarks_bar.add_bookmark_btn(display_title, url)

    def create_status_bar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        self.status.setStyleSheet(f"QStatusBar {{ background-color: {self.bg_color}; color: {self.text_color}; }}")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(120)
        self.progress_bar.setMaximumHeight(14)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                font-size: 9px;
                background-color: {self.base_color};
                color: {self.text_color};
                border: 1px solid #444444;
                border-radius: 2px;
                text-align: center;
            }}
            QProgressBar::chunk {{ background-color: {self.accent_color}; }}
        """)
        self.status.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()

    def navigate_to_url(self):
        browser = self.current_browser()
        if browser:
            url = self.address_bar.text()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            browser.setUrl(QUrl(url))

    def execute_search(self):
        browser = self.current_browser()
        if browser:
            query = self.search_bar.text()
            if query:
                base_url = self.search_engines.get(self.search_engine, "https://duckduckgo.com/?q=")
                browser.setUrl(QUrl(f"{base_url}{query}"))

    def update_address_bar(self, qurl):
        self.address_bar.setText(qurl.toString())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.find_bar.isVisible():
            self.find_bar.close_find_bar()
        else:
            super().keyPressEvent(event)