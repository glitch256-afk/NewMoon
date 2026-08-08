from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from PyQt6.QtWebEngineCore import QWebEnginePage

class FindBar(QFrame):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedHeight(34)
        
        self.apply_styles()
        self.init_ui()
        self.hide()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.main_window.bg_color};
                border-top: 1px solid #444444;
                color: {self.main_window.text_color};
            }}
            QLineEdit {{
                padding: 2px 6px;
                max-height: 22px;
                font-size: 12px;
                background-color: {self.main_window.base_color};
                color: {self.main_window.text_color};
                border: 1px solid #444444;
                border-radius: 3px;
            }}
            QPushButton {{
                max-height: 22px;
                padding: 0px 8px;
                font-size: 11px;
                background: transparent;
                border: 1px solid transparent;
                color: {self.main_window.text_color};
            }}
            QPushButton:hover {{
                background-color: {self.main_window.accent_hover};
                border: 1px solid {self.main_window.accent_color};
            }}
        """)

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(6)

        find_label = QLabel("Find:")
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find in page...")
        self.find_input.textChanged.connect(self.find_text_next)
        self.find_input.returnPressed.connect(self.find_text_next)

        next_btn = QPushButton("Next 🔽")
        next_btn.clicked.connect(self.find_text_next)

        prev_btn = QPushButton("Previous 🔼")
        prev_btn.clicked.connect(self.find_text_prev)

        self.case_checkbox = QCheckBox("Match Case")
        self.case_checkbox.setStyleSheet("font-size: 11px;")
        self.case_checkbox.stateChanged.connect(self.find_text_next)

        close_btn = QPushButton("✖")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close_find_bar)

        layout.addWidget(find_label)
        layout.addWidget(self.find_input)
        layout.addWidget(next_btn)
        layout.addWidget(prev_btn)
        layout.addWidget(self.case_checkbox)
        layout.addStretch()
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def show_find_bar(self):
        self.show()
        self.find_input.setFocus()
        self.find_input.selectAll()

    def close_find_bar(self):
        self.hide()
        browser = self.main_window.current_browser()
        if browser:
            browser.findText("")

    def find_text_next(self):
        browser = self.main_window.current_browser()
        text = self.find_input.text()
        if browser and text:
            flags = QWebEnginePage.FindFlag(0)
            if self.case_checkbox.isChecked():
                flags |= QWebEnginePage.FindFlag.FindCaseSensitively
            browser.findText(text, flags)

    def find_text_prev(self):
        browser = self.main_window.current_browser()
        text = self.find_input.text()
        if browser and text:
            flags = QWebEnginePage.FindFlag.FindBackward
            if self.case_checkbox.isChecked():
                flags |= QWebEnginePage.FindFlag.FindCaseSensitively
            browser.findText(text, flags)