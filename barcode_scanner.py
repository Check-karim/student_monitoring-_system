import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from pyzbar.pyzbar import decode
import requests

class BarcodeScanner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Barcode Scanner")
        self.setGeometry(100, 100, 640, 480)

        self.label = QLabel(self)
        self.label.resize(640, 480)

        self.start_button = QPushButton("Start Camera", self)
        self.start_button.clicked.connect(self.start_camera)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.start_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.cap = None

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(20)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame to an image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            decoded_objects = decode(frame)

            for obj in decoded_objects:
                points = obj.polygon
                # Draw rectangle around barcode
                if len(points) == 4:
                    cv2.polylines(frame, [np.array(points, np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)
                # Extract barcode data
                barcode_data = obj.data.decode("utf-8")
                self.send_barcode_to_flask(barcode_data)
                self.timer.stop()
                self.cap.release()
                break

            # Display the frame in the GUI
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(image)
            self.label.setPixmap(pix)

    def send_barcode_to_flask(self, barcode_data):
        # Send barcode to Flask backend
        try:
            response = requests.post("http://127.0.0.1:5000/barcode_login", data={'barcode': barcode_data})
            if response.status_code == 200:
                print("Barcode sent successfully")
            else:
                print("Failed to send barcode")
        except Exception as e:
            print(f"Error sending barcode: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarcodeScanner()
    window.show()
    sys.exit(app.exec_())
