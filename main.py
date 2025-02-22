from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QPushButton
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtCore import Qt, QRect
import sys
import os
import xml.etree.ElementTree
import datetime
from qt_material import apply_stylesheet
import resources_rc  # Import the compiled resource file

class DragDropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TeleScan to Coe File GUI")
        self.setFixedSize(300, 200)
        self.setWindowIcon(QIcon(":/icons/icon.ico"))
        self.center_window()

        self.label = QLabel("Drag your .tlscan file in", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

        self.about_button = QPushButton("About", self)
        self.about_button.setGeometry(100, 150, 100, 30)  # Move to middle bottom
        self.about_button.clicked.connect(self.show_about)

        self.setAcceptDrops(True)

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.setGeometry(QRect(x, y, self.width(), self.height()))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()  # Get the first file path
            self.label.setText("success convert to: output.coe")  # Display file path
            print("Dropped file:", file_path)  # Process the file
            self.convert_tlscan_to_coe(file_path)

    # steal from: https://github.com/Rakeshmonkee/DMA/blob/main/.tlscan%20to%20.coe/telescan_to_coe.py
    def convert_tlscan_to_coe(self, src_path):
        try:
            dst_path = os.path.normpath(os.getcwd() + "/output.coe")

            # Load and parse the XML format '.tlscan' file
            bs = xml.etree.ElementTree.parse(str(src_path)).find('.//bytes').text

            # Make one 8,192 char long hex bytes string
            bs = ''.join(bs.split())
            assert len(bs) == 8192, f'Expected 8192 character (4096 hex byte) string, got {len(bs):,}!'

            # Write out ".coe" file
            with open(dst_path, 'w') as fp:
                fp.write(f'\n; Converted to COE from "{src_path}" on {datetime.datetime.now()}\n')
                fp.write('memory_initialization_radix=16;\nmemory_initialization_vector=\n')

                for y in range(16):
                    fp.write(f'\n; {(y * 256):04X}\n')

                    for x in range(16):
                        fp.write(f'{bs[0:8]},{bs[8:16]},{bs[16:24]},{bs[24:32]},\n')
                        bs = bs[32:]

                fp.write(';\n')
            print("COE file saved to:", dst_path)
            QMessageBox.information(self, "Success", f"Conversion complete!\nCOE file saved to: {dst_path}")
        except Exception as e:
            self.label.setText("failed converting target file")  # Display file path
            QMessageBox.critical(self, "Error", f"Conversion failed!\n{str(e)}")
            print("Conversion failed:", str(e))

    def show_about(self):
        QMessageBox.information(self, "About",
                                "This tool converts .tlscan XML files to .coe format.\nDeveloped by un4ckn0wl3z.\nGithub: https://github.com/un4ckn0wl3z")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # setup stylesheet
    apply_stylesheet(app, theme='dark_teal.xml')
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec())
