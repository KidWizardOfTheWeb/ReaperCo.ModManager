from PyQt6.QtWidgets import QLabel, QVBoxLayout, QDialog, QDialogButtonBox
class WarningWindow(QDialog):
    def __init__(self, parent=None, title="ERROR", warning_text="Undefined error, process may continue with weird behavior or fail entirely. Good luck."):
        super().__init__(parent)
        # Used for any error popups that can occur, or general information

        self.setWindowTitle(title)

        QBtn = (
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(warning_text)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)