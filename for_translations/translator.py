import hashlib
import binascii
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox)
import sys

class TranslatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JAR File Translator")
        self.setGeometry(100, 100, 400, 90)

        # Default values
        self.name = "RS Infinity Booster"
        self.version = "1.16.5"
        self.jar_file = "1.jar"
        self.translated_file = "Tr.jar"

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Version input
        version_layout = QHBoxLayout()
        version_label = QLabel("Version:")
        self.version_input = QLineEdit(self.version)
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_input)
        layout.addLayout(version_layout)

        # JAR file input
        jar_layout = QHBoxLayout()
        jar_label = QLabel("JAR File:")
        self.jar_file_input = QLineEdit(self.jar_file)
        jar_button = QPushButton("Browse")
        jar_button.clicked.connect(self.browse_jar_file)
        jar_layout.addWidget(jar_label)
        jar_layout.addWidget(self.jar_file_input)
        jar_layout.addWidget(jar_button)
        layout.addLayout(jar_layout)

        # Translated file input
        translated_layout = QHBoxLayout()
        translated_label = QLabel("Translated File:")
        self.translated_file_input = QLineEdit(self.translated_file)
        translated_button = QPushButton("Browse")
        translated_button.clicked.connect(self.browse_translated_file)
        translated_layout.addWidget(translated_label)
        translated_layout.addWidget(self.translated_file_input)
        translated_layout.addWidget(translated_button)
        layout.addLayout(translated_layout)

        # Action buttons
        generate_button = QPushButton("Generate")
        generate_button.clicked.connect(self.run_main)
        layout.addWidget(generate_button)

        layout.addStretch()

    def browse_jar_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JAR File", "", "JAR Files (*.jar)")
        if file_path:
            self.jar_file_input.setText(file_path)

    def browse_translated_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Translated JAR File", "", "JAR Files (*.jar)")
        if file_path:
            self.translated_file_input.setText(file_path)

    def generate_sha256(self, file_path):
        """Generate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def file_to_hex(self, file_path):
        """Convert file to hexadecimal string."""
        with open(file_path, "rb") as f:
            content = f.read()
        return binascii.hexlify(content).decode('utf-8')

    def run_clean(self):
        try:
            jar_file = self.jar_file_input.text()
            for file in [f"{jar_file}.sha256", "sha256.json"]:
                if os.path.exists(file):
                    os.remove(file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during cleanup: {str(e)}")

    def run_main(self):
        try:
            jar_file = self.jar_file_input.text()
            translated_file = self.translated_file_input.text()
            name = self.name_input.text()
            version = self.version_input.text()

            # Validate inputs
            if not os.path.exists(jar_file):
                QMessageBox.critical(self, "Error", f"JAR file '{jar_file}' does not exist")
                return
            if not os.path.exists(translated_file):
                QMessageBox.critical(self, "Error", f"Translated file '{translated_file}' does not exist")
                return
            if not name:
                QMessageBox.critical(self, "Error", "Name cannot be empty")
                return
            if not version:
                QMessageBox.critical(self, "Error", "Version cannot be empty")
                return

            # Generate SHA256 hash and save to file
            sha256sum = self.generate_sha256(jar_file)

            # Convert translated jar to hex
            hex_content = self.file_to_hex(translated_file)

            # Create JSON data
            json_data = {
                "name": name,
                "version": version,
                "file": hex_content
            }

            # Write JSON to file
            with open(f"{sha256sum}.json", "w") as f:
                json.dump(json_data, f, indent=2)

            self.run_clean()
            QMessageBox.information(self, "Success", "Files generated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorGUI()
    window.show()
    sys.exit(app.exec_())
