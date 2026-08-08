from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QSpinBox, QDialogButtonBox

class PreferencesDialog(QDialog):
    def __init__(self, current_home, current_padding, current_engine, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.home_input = QLineEdit(current_home)
        form_layout.addRow("Homepage URL:", self.home_input)

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["DuckDuckGo", "Google", "Bing", "Brave"])
        self.engine_combo.setCurrentText(current_engine)
        form_layout.addRow("Default Search Engine:", self.engine_combo)

        self.padding_input = QSpinBox()
        self.padding_input.setRange(0, 50)
        self.padding_input.setValue(current_padding)
        self.padding_input.setSuffix(" px")
        form_layout.addRow("Web View Padding:", self.padding_input)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_settings(self):
        return {
            "home_url": self.home_input.text(),
            "padding": self.padding_input.value(),
            "engine": self.engine_combo.currentText()
        }