from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel, QFrame, QHBoxLayout, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt

class AvalancheVisualizer(QWidget):
    run_test_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        frame = QFrame()
        frame.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 10px;")
        inner_layout = QVBoxLayout(frame)

        lbl_title = QLabel("🧪 PHÂN TÍCH THUẬT TOÁN DES")
        lbl_title.setStyleSheet("font-weight: bold; color: #ffffff;")
        inner_layout.addWidget(lbl_title)

        lbl_desc = QLabel("Hiệu ứng Tuyết lở: Thay đổi 1 bit đầu vào -> Đo lường % thay đổi đầu ra")
        lbl_desc.setStyleSheet("color: #aaa; font-size: 11px;")
        inner_layout.addWidget(lbl_desc)

        # --- INPUT A & B (ĐÃ XÓA GIÁ TRỊ MẶC ĐỊNH) ---
        input_layout = QHBoxLayout()
        
        self.input_a = QLineEdit()
        self.input_a.setPlaceholderText("Nhập PIN A...")
        self.input_a.setStyleSheet("background-color: #333; color: white; border: 1px solid #555; padding: 3px;")
        
        self.input_b = QLineEdit()
        self.input_b.setPlaceholderText("Nhập PIN B...")
        self.input_b.setStyleSheet("background-color: #333; color: white; border: 1px solid #555; padding: 3px;")
        
        input_layout.addWidget(QLabel("Input A:"))
        input_layout.addWidget(self.input_a)
        input_layout.addWidget(QLabel("Input B:"))
        input_layout.addWidget(self.input_b)
        inner_layout.addLayout(input_layout)
        # ---------------------------------------------

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("Chờ dữ liệu...")
        self.progress.setFixedHeight(25)
        inner_layout.addWidget(self.progress)

        self.btn_run = QPushButton("⚡ CHẠY KIỂM THỬ")
        self.btn_run.setObjectName("BtnAvalanche")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.clicked.connect(self.emit_signal)
        inner_layout.addWidget(self.btn_run)

        layout.addWidget(frame)
        self.setLayout(layout)

    def emit_signal(self):
        pin_a = self.input_a.text()
        pin_b = self.input_b.text()
        self.run_test_signal.emit(pin_a, pin_b)

    def update_progress(self, percent):
        self.progress.setValue(int(percent))
        if 40 <= percent <= 60:
             self.progress.setFormat(f"{percent:.2f}% - TỐT (Bảo mật cao)")
        else:
             self.progress.setFormat(f"{percent:.2f}% - YẾU (Trùng lặp)")